/**
 * Neural Network Visualization - Interactive 3D network using Three.js
 */

import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import type { NetworkArchitecture } from '../../../services/mock-data/ml-model-data';
import { calculateTotalParams } from '../../../services/mock-data/ml-model-data';
import { Panel, PanelHeader, PanelContent } from '../../../components/common/Panel';

export function NeuralNetworkVisualization({ architecture }: { architecture: NetworkArchitecture }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = 500;

    // Initialize Three.js scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e1a);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.z = 8;
    camera.position.y = 2;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Orbit controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enableZoom = true;
    controlsRef.current = controls;

    // Build network visualization
    const networkGroup = buildNetworkMesh(architecture);
    scene.add(networkGroup);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    const pointLight1 = new THREE.PointLight(0x00ff88, 1, 100);
    pointLight1.position.set(10, 10, 10);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0x00ddff, 0.5, 100);
    pointLight2.position.set(-10, -5, 5);
    scene.add(pointLight2);

    // Animation loop
    let animationTime = 0;
    function animate() {
      requestAnimationFrame(animate);
      controls.update();

      // Animate forward pass
      animationTime += 0.02;
      animateForwardPass(networkGroup, animationTime);

      renderer.render(scene, camera);
    }
    animate();

    // Resize handler
    const handleResize = () => {
      if (!containerRef.current) return;
      const newWidth = containerRef.current.clientWidth;
      camera.aspect = newWidth / height;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, height);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
      controls.dispose();
      if (containerRef.current) {
        containerRef.current.removeChild(renderer.domElement);
      }
    };
  }, [architecture]);

  return (
    <Panel>
      <PanelHeader>
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">Neural Network Architecture</h3>
            <div className="text-sm text-gray-400">Interactive 3D Visualization</div>
          </div>
          <div className="text-sm text-gray-400">
            Layers: {architecture.layers.length} | Params: {calculateTotalParams(architecture)}
          </div>
        </div>
      </PanelHeader>
      <PanelContent>
        <div ref={containerRef} className="rounded overflow-hidden" />

        <div className="mt-4 grid grid-cols-3 gap-3 text-sm">
          <div className="bg-gray-800 rounded p-2">
            <div className="text-xs text-gray-400 mb-1">Input</div>
            <div className="font-mono text-lg text-green-400">{architecture.layers[0].neurons}</div>
          </div>
          <div className="bg-gray-800 rounded p-2">
            <div className="text-xs text-gray-400 mb-1">Hidden</div>
            <div className="font-mono text-lg text-blue-400">{architecture.layers.length - 2}</div>
          </div>
          <div className="bg-gray-800 rounded p-2">
            <div className="text-xs text-gray-400 mb-1">Output</div>
            <div className="font-mono text-lg text-yellow-400">
              {architecture.layers[architecture.layers.length - 1].neurons}
            </div>
          </div>
        </div>

        <div className="mt-2 text-xs text-gray-500 text-center">
          Drag to rotate • Scroll to zoom
        </div>
      </PanelContent>
    </Panel>
  );
}

function buildNetworkMesh(architecture: NetworkArchitecture): THREE.Group {
  const group = new THREE.Group();

  const layerSpacing = 3;
  const maxNeurons = Math.max(...architecture.layers.map((l) => l.neurons));
  const neuronSpacing = Math.min(0.5, 8 / maxNeurons); // Adaptive spacing

  // Create neurons for each layer
  architecture.layers.forEach((layer, layerIndex) => {
    const x = (layerIndex - architecture.layers.length / 2) * layerSpacing;

    // Sample neurons if layer is too large (display max 20 neurons per layer)
    const displayNeurons = Math.min(layer.neurons, 20);
    const step = layer.neurons > 20 ? Math.floor(layer.neurons / 20) : 1;

    for (let neuronIndex = 0; neuronIndex < displayNeurons; neuronIndex++) {
      const actualIndex = neuronIndex * step;
      const y = (neuronIndex - displayNeurons / 2) * neuronSpacing;

      // Create neuron sphere
      const geometry = new THREE.SphereGeometry(0.12, 16, 16);
      const material = new THREE.MeshPhongMaterial({
        color: 0x00ff88,
        emissive: 0x00ff88,
        emissiveIntensity: 0.2,
        shininess: 100,
      });
      const neuron = new THREE.Mesh(geometry, material);
      neuron.position.set(x, y, 0);

      // Store metadata
      neuron.userData = {
        layer: layerIndex,
        neuron: actualIndex,
        activation: 0,
      };

      group.add(neuron);

      // Create connections to next layer (sample connections for large layers)
      if (layerIndex < architecture.layers.length - 1) {
        const nextLayer = architecture.layers[layerIndex + 1];
        const nextX = x + layerSpacing;
        const nextDisplayNeurons = Math.min(nextLayer.neurons, 20);
        const nextStep = nextLayer.neurons > 20 ? Math.floor(nextLayer.neurons / 20) : 1;

        // Sample connections (not all-to-all for large networks)
        const connectionSamples = Math.min(5, nextDisplayNeurons);
        for (let i = 0; i < connectionSamples; i++) {
          const nextNeuronIndex = Math.floor((i * nextDisplayNeurons) / connectionSamples);
          const nextActualIndex = nextNeuronIndex * nextStep;
          const nextY = (nextNeuronIndex - nextDisplayNeurons / 2) * neuronSpacing;

          // Get weight (if available)
          const weight =
            architecture.weights[layerIndex]?.[actualIndex]?.[nextActualIndex] || Math.random() - 0.5;

          // Create connection line
          const points = [new THREE.Vector3(x, y, 0), new THREE.Vector3(nextX, nextY, 0)];
          const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
          const lineMaterial = new THREE.LineBasicMaterial({
            color: weight > 0 ? 0x00ff88 : 0xff4444,
            opacity: Math.min(0.4, Math.abs(weight) * 0.8),
            transparent: true,
          });
          const line = new THREE.Line(lineGeometry, lineMaterial);
          line.userData = { weight };
          group.add(line);
        }
      }
    }
  });

  return group;
}

function animateForwardPass(networkMesh: THREE.Group, time: number) {
  // Simulate forward pass animation with wave effect
  const wave = Math.sin(time) * 0.5 + 0.5;

  networkMesh.children.forEach((child) => {
    if (child instanceof THREE.Mesh && child.userData.layer !== undefined) {
      const layer = child.userData.layer;
      const phaseShift = layer * 0.3;
      const activation = Math.sin(time + phaseShift) * 0.5 + 0.5;

      // Pulse neurons based on activation
      const material = child.material as THREE.MeshPhongMaterial;
      material.emissiveIntensity = activation * 0.6;

      // Subtle scale pulse
      const scale = 1 + activation * 0.2;
      child.scale.set(scale, scale, scale);
    }
  });

  // Gently rotate the entire network
  networkMesh.rotation.y = Math.sin(time * 0.1) * 0.1;
}
