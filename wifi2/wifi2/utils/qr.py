import numpy
import pyqrcode
import png


def wifi_qr(ssid: str, security: str, password: str):
    """
    Create WiFi QR code object
    """
    qr = pyqrcode.create(f'WIFI:S:{ssid};T:{security};P:{password};;')
    return qr


def qr2array(qr):
    """
    Convert QR code object into array representation.
    """
    arr = []
    for line in qr.text().split('\n'):
        if line:
            arr.append(list(map(int, line)))
    return numpy.vstack(arr)


def png_b64(qr, scale: int = 10):
    """
    Return base64 encoded PNG of QR code.
    """
    return qr.png_data_uri(scale=scale)

