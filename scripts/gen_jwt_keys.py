#!/usr/bin/env python3
"""
Generate RS256 key pair for JWT signing.

Usage:
    python gen_jwt_keys.py --output-dir ./keys

This script generates 'private_key.pem' and 'public_key.pem' in the specified directory.
"""

import argparse
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_keys(output_dir: Path):
    """Generate and save RSA private and public keys."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,  # Standard size
    )

    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),  # Store securely in prod!
    )

    # Get public key
    public_key = private_key.public_key()

    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # Write keys to files
    private_path = output_dir / "private_key.pem"
    public_path = output_dir / "public_key.pem"

    with open(private_path, "wb") as f:
        f.write(private_pem)
    print(f"Private key saved to: {private_path}")

    with open(public_path, "wb") as f:
        f.write(public_pem)
    print(f"Public key saved to: {public_path}")

    print("\nRemember to:")
    print("- Securely store the private key (e.g., in environment variables or a secrets manager)")
    print("- Add the public key path or value to your settings for token verification.")


def main():
    parser = argparse.ArgumentParser(description="Generate RS256 key pair for JWT.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./keys",
        help="Directory to save the generated keys (default: ./keys)",
    )

    args = parser.parse_args()
    output_path = Path(args.output_dir)

    generate_keys(output_path)


if __name__ == "__main__":
    main()
