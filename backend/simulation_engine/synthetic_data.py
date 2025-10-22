# synthetic_data.py - Synthetic data generation using GAN and VAE

import numpy as np
import pandas as pd
from typing import Dict, Tuple
import logging
import torch
import torch.nn as nn
import torch.optim as optim
from scipy import stats
from config import Config
from utils import validate_returns

logger = logging.getLogger(__name__)


class TimeSeriesGAN:
    """
    Generative Adversarial Network for time series generation.

    Learns to generate realistic synthetic price paths.
    """

    def __init__(self, sequence_length: int = 100, latent_dim: int = 100):
        """
        Args:
            sequence_length: Length of time series to generate
            latent_dim: Dimension of latent noise vector
        """
        self.sequence_length = sequence_length
        self.latent_dim = latent_dim

        # Generator network
        self.generator = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, sequence_length),
            nn.Tanh()
        )

        # Discriminator network
        self.discriminator = nn.Sequential(
            nn.Linear(sequence_length, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 128),
            nn.LeakyReLU(0.2),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.generator.to(self.device)
        self.discriminator.to(self.device)

    def train(
        self,
        real_data: np.ndarray,
        epochs: int = None,
        batch_size: int = None,
        learning_rate: float = None
    ) -> Dict:
        """
        Train GAN on real data.

        Args:
            real_data: Real time series data (n_samples, sequence_length)
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate

        Returns:
            Dictionary with training history
        """
        if epochs is None:
            epochs = Config.GAN_EPOCHS
        if batch_size is None:
            batch_size = Config.GAN_BATCH_SIZE
        if learning_rate is None:
            learning_rate = Config.GAN_LEARNING_RATE

        logger.info(f"Training TimeSeriesGAN (epochs={epochs})")

        # Optimizers
        g_optimizer = optim.Adam(self.generator.parameters(), lr=learning_rate)
        d_optimizer = optim.Adam(self.discriminator.parameters(), lr=learning_rate)

        # Loss function
        criterion = nn.BCELoss()

        # Training history
        g_losses = []
        d_losses = []

        for epoch in range(epochs):
            # Prepare batches
            n_batches = len(real_data) // batch_size

            epoch_g_loss = 0
            epoch_d_loss = 0

            for batch_idx in range(n_batches):
                # Get real batch
                batch_start = batch_idx * batch_size
                batch_end = batch_start + batch_size
                real_batch = real_data[batch_start:batch_end]
                real_batch = torch.FloatTensor(real_batch).to(self.device)

                batch_size_actual = len(real_batch)

                # Labels
                real_labels = torch.ones(batch_size_actual, 1).to(self.device)
                fake_labels = torch.zeros(batch_size_actual, 1).to(self.device)

                # Train Discriminator
                d_optimizer.zero_grad()

                # Real samples
                d_real = self.discriminator(real_batch)
                d_real_loss = criterion(d_real, real_labels)

                # Fake samples
                noise = torch.randn(batch_size_actual, self.latent_dim).to(self.device)
                fake_batch = self.generator(noise)
                d_fake = self.discriminator(fake_batch.detach())
                d_fake_loss = criterion(d_fake, fake_labels)

                d_loss = d_real_loss + d_fake_loss
                d_loss.backward()
                d_optimizer.step()

                # Train Generator
                g_optimizer.zero_grad()

                noise = torch.randn(batch_size_actual, self.latent_dim).to(self.device)
                fake_batch = self.generator(noise)
                d_fake = self.discriminator(fake_batch)
                g_loss = criterion(d_fake, real_labels)  # Generator wants discriminator to think it's real

                g_loss.backward()
                g_optimizer.step()

                epoch_g_loss += g_loss.item()
                epoch_d_loss += d_loss.item()

            # Average losses for epoch
            avg_g_loss = epoch_g_loss / n_batches
            avg_d_loss = epoch_d_loss / n_batches

            g_losses.append(avg_g_loss)
            d_losses.append(avg_d_loss)

            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}/{epochs}: G_loss={avg_g_loss:.4f}, D_loss={avg_d_loss:.4f}")

        logger.info("TimeSeriesGAN training completed")

        return {
            'g_losses': g_losses,
            'd_losses': d_losses,
            'epochs': epochs
        }

    def generate(self, n_samples: int = 1000) -> np.ndarray:
        """
        Generate synthetic time series.

        Args:
            n_samples: Number of samples to generate

        Returns:
            Generated samples (n_samples, sequence_length)
        """
        self.generator.eval()

        with torch.no_grad():
            noise = torch.randn(n_samples, self.latent_dim).to(self.device)
            generated = self.generator(noise)
            generated = generated.cpu().numpy()

        logger.info(f"Generated {n_samples} synthetic time series samples")

        return generated


class TimeSeriesVAE:
    """
    Variational Autoencoder for time series generation.

    Learns a probabilistic latent representation of time series.
    """

    def __init__(self, sequence_length: int = 100, latent_dim: int = 10):
        """
        Args:
            sequence_length: Length of time series
            latent_dim: Dimension of latent space
        """
        self.sequence_length = sequence_length
        self.latent_dim = latent_dim

        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(sequence_length, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU()
        )

        self.fc_mu = nn.Linear(64, latent_dim)
        self.fc_logvar = nn.Linear(64, latent_dim)

        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, sequence_length),
            nn.Tanh()
        )

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.encoder.to(self.device)
        self.fc_mu.to(self.device)
        self.fc_logvar.to(self.device)
        self.decoder.to(self.device)

    def encode(self, x):
        """Encode input to latent distribution parameters."""
        h = self.encoder(x)
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar

    def reparameterize(self, mu, logvar):
        """Reparameterization trick."""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        """Decode latent vector to output."""
        return self.decoder(z)

    def forward(self, x):
        """Forward pass through VAE."""
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z)
        return recon, mu, logvar

    def loss_function(self, recon_x, x, mu, logvar):
        """VAE loss: reconstruction + KL divergence."""
        recon_loss = nn.functional.mse_loss(recon_x, x, reduction='sum')
        kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        return recon_loss + kl_loss

    def train(
        self,
        real_data: np.ndarray,
        epochs: int = None,
        batch_size: int = None,
        learning_rate: float = None
    ) -> Dict:
        """
        Train VAE on real data.

        Args:
            real_data: Real time series data
            epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate

        Returns:
            Dictionary with training history
        """
        if epochs is None:
            epochs = Config.GAN_EPOCHS
        if batch_size is None:
            batch_size = Config.GAN_BATCH_SIZE
        if learning_rate is None:
            learning_rate = Config.GAN_LEARNING_RATE

        logger.info(f"Training TimeSeriesVAE (epochs={epochs})")

        optimizer = optim.Adam(
            list(self.encoder.parameters()) +
            list(self.fc_mu.parameters()) +
            list(self.fc_logvar.parameters()) +
            list(self.decoder.parameters()),
            lr=learning_rate
        )

        losses = []

        for epoch in range(epochs):
            epoch_loss = 0
            n_batches = len(real_data) // batch_size

            for batch_idx in range(n_batches):
                batch_start = batch_idx * batch_size
                batch_end = batch_start + batch_size
                batch = real_data[batch_start:batch_end]
                batch = torch.FloatTensor(batch).to(self.device)

                optimizer.zero_grad()

                recon_batch, mu, logvar = self.forward(batch)
                loss = self.loss_function(recon_batch, batch, mu, logvar)

                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()

            avg_loss = epoch_loss / n_batches
            losses.append(avg_loss)

            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}/{epochs}: Loss={avg_loss:.4f}")

        logger.info("TimeSeriesVAE training completed")

        return {'losses': losses, 'epochs': epochs}

    def generate(self, n_samples: int = 1000) -> np.ndarray:
        """
        Generate synthetic time series by sampling from latent space.

        Args:
            n_samples: Number of samples to generate

        Returns:
            Generated samples
        """
        self.decoder.eval()

        with torch.no_grad():
            z = torch.randn(n_samples, self.latent_dim).to(self.device)
            generated = self.decoder(z)
            generated = generated.cpu().numpy()

        logger.info(f"Generated {n_samples} synthetic time series samples (VAE)")

        return generated


def timeseries_gan(
    returns: pd.Series,
    n_samples: int = 1000,
    epochs: int = None
) -> Dict:
    """
    Generate synthetic returns using GAN.

    Args:
        returns: Real returns time series
        n_samples: Number of synthetic samples to generate
        epochs: Training epochs

    Returns:
        Dictionary with synthetic data and validation metrics
    """
    returns = validate_returns(returns)

    if epochs is None:
        epochs = Config.GAN_EPOCHS

    # Prepare data: create sliding windows
    sequence_length = 100
    real_sequences = []

    for i in range(len(returns) - sequence_length + 1):
        sequence = returns.iloc[i:i + sequence_length].values
        real_sequences.append(sequence)

    real_sequences = np.array(real_sequences)

    # Normalize data to [-1, 1]
    data_min = real_sequences.min()
    data_max = real_sequences.max()
    real_sequences_normalized = 2 * (real_sequences - data_min) / (data_max - data_min) - 1

    # Train GAN
    gan = TimeSeriesGAN(sequence_length=sequence_length)
    training_history = gan.train(real_sequences_normalized, epochs=epochs)

    # Generate synthetic data
    synthetic_normalized = gan.generate(n_samples)

    # Denormalize
    synthetic_data = (synthetic_normalized + 1) * (data_max - data_min) / 2 + data_min

    # Validate synthetic data
    validation = validate_synthetic_data(returns.values, synthetic_data.flatten())

    logger.info(f"GAN synthetic data generation completed: {n_samples} samples")

    return {
        'synthetic_data': synthetic_data,
        'training_history': training_history,
        'validation': validation,
        'method': 'GAN'
    }


def vae_market_data(
    returns_matrix: pd.DataFrame,
    latent_dim: int = None,
    n_samples: int = 1000,
    epochs: int = None
) -> Dict:
    """
    Generate synthetic multi-asset returns using VAE.

    Args:
        returns_matrix: DataFrame of returns for multiple assets
        latent_dim: Latent space dimension
        n_samples: Number of synthetic samples
        epochs: Training epochs

    Returns:
        Dictionary with synthetic data and validation metrics
    """
    if latent_dim is None:
        latent_dim = Config.VAE_LATENT_DIM
    if epochs is None:
        epochs = Config.GAN_EPOCHS

    # Prepare data
    returns_array = returns_matrix.values

    # Normalize
    data_mean = returns_array.mean(axis=0)
    data_std = returns_array.std(axis=0)
    returns_normalized = (returns_array - data_mean) / (data_std + 1e-8)

    # Train VAE
    vae = TimeSeriesVAE(sequence_length=returns_array.shape[1], latent_dim=latent_dim)
    training_history = vae.train(returns_normalized, epochs=epochs)

    # Generate synthetic data
    synthetic_normalized = vae.generate(n_samples)

    # Denormalize
    synthetic_data = synthetic_normalized * (data_std + 1e-8) + data_mean

    # Validate
    validation_results = {}
    for i, col in enumerate(returns_matrix.columns):
        validation_results[col] = validate_synthetic_data(
            returns_array[:, i],
            synthetic_data[:, i]
        )

    logger.info(f"VAE synthetic data generation completed: {n_samples} samples, {returns_array.shape[1]} assets")

    return {
        'synthetic_data': synthetic_data,
        'training_history': training_history,
        'validation': validation_results,
        'method': 'VAE',
        'asset_names': list(returns_matrix.columns)
    }


def validate_synthetic_data(
    real_data: np.ndarray,
    synthetic_data: np.ndarray
) -> Dict:
    """
    Validate synthetic data against real data using statistical tests.

    Args:
        real_data: Real data array
        synthetic_data: Synthetic data array

    Returns:
        Dictionary with validation test results
    """
    # Kolmogorov-Smirnov test
    ks_statistic, ks_pvalue = stats.ks_2samp(real_data, synthetic_data)

    # Moments comparison
    real_mean = np.mean(real_data)
    real_std = np.std(real_data)
    real_skew = stats.skew(real_data)
    real_kurt = stats.kurtosis(real_data)

    synth_mean = np.mean(synthetic_data)
    synth_std = np.std(synthetic_data)
    synth_skew = stats.skew(synthetic_data)
    synth_kurt = stats.kurtosis(synthetic_data)

    # Autocorrelation comparison (lag 1)
    real_autocorr = np.corrcoef(real_data[:-1], real_data[1:])[0, 1]
    synth_autocorr = np.corrcoef(synthetic_data[:-1], synthetic_data[1:])[0, 1]

    return {
        'ks_statistic': ks_statistic,
        'ks_pvalue': ks_pvalue,
        'ks_passed': ks_pvalue > 0.05,  # Accept if p > 0.05
        'moments': {
            'real': {'mean': real_mean, 'std': real_std, 'skew': real_skew, 'kurt': real_kurt},
            'synthetic': {'mean': synth_mean, 'std': synth_std, 'skew': synth_skew, 'kurt': synth_kurt},
            'differences': {
                'mean_diff': abs(real_mean - synth_mean),
                'std_diff': abs(real_std - synth_std),
                'skew_diff': abs(real_skew - synth_skew),
                'kurt_diff': abs(real_kurt - synth_kurt)
            }
        },
        'autocorrelation': {
            'real': real_autocorr,
            'synthetic': synth_autocorr,
            'difference': abs(real_autocorr - synth_autocorr)
        }
    }
