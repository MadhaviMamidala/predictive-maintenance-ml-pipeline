#!/usr/bin/env python3
"""
SSL Certificate Generator for Windows
Generates self-signed SSL certificates for development/production use
"""

import os
import sys
import ipaddress
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta

def generate_ssl_certificates(domain="localhost", days=365):
    """Generate self-signed SSL certificates"""
    
    # Create SSL directory if it doesn't exist
    ssl_dir = Path("nginx/ssl")
    ssl_dir.mkdir(parents=True, exist_ok=True)
    
    cert_path = ssl_dir / "cert.pem"
    key_path = ssl_dir / "key.pem"
    
    # Check if certificates already exist
    if cert_path.exists() and key_path.exists():
        print("✓ SSL certificates already exist")
        return
    
    print("Generating SSL certificates...")
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Organization"),
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=days)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(domain),
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Write private key
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Write certificate
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print("✓ SSL certificates generated successfully")
    print(f"  Certificate: {cert_path}")
    print(f"  Private Key: {key_path}")

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
    
    try:
        generate_ssl_certificates(domain, days)
    except Exception as e:
        print(f"Error generating SSL certificates: {e}")
        sys.exit(1) 