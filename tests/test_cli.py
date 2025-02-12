from unittest.mock import patch
from io import StringIO
import sys
from dns_prove.cli import DNSProveCLI

def test_cli_commands():
    """Test CLI command execution"""
    cli = DNSProveCLI()
    
    # Test verify command
    with patch('sys.stdout', new=StringIO()) as fake_out:
        cli.onecmd('verify test.eth')
        output = fake_out.getvalue()
        assert "Verifying" in output
    
    # Test batch command
    with patch('sys.stdout', new=StringIO()) as fake_out:
        cli.onecmd('batch test_domains.txt')
        output = fake_out.getvalue()
        assert "Processed" in output
    
    # Test network switching
    with patch('sys.stdout', new=StringIO()) as fake_out:
        cli.onecmd('network testnet')
        output = fake_out.getvalue()
        assert "Switched to testnet" in output

def test_cli_aliases():
    """Test CLI command aliases"""
    cli = DNSProveCLI()
    
    # Test verify alias
    with patch('sys.stdout', new=StringIO()) as fake_out:
        cli.onecmd('v test.eth')
        verify_output = fake_out.getvalue()
    
    with patch('sys.stdout', new=StringIO()) as fake_out:
        cli.onecmd('verify test.eth')
        full_output = fake_out.getvalue()
    
    assert verify_output == full_output 