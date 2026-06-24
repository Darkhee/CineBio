import re
from django.core.exceptions import ValidationError


def validar_documento(tipo_documento, documento):
 
    doc = (documento or '').strip().upper().replace('.', '').replace(' ', '')

    if tipo_documento == 'RUT':
        if not re.match(r'^\d{8}-[0-9K]$', doc):
            raise ValidationError(
                'El RUT debe tener 8 dígitos, guion y dígito verificador (ej: 12345678-9 o 12345678-K).'
            )
    elif tipo_documento == 'PASAPORTE':
        if not re.match(r'^[A-Z0-9]{3,}$', doc):
            raise ValidationError('Ingresa un número de pasaporte válido (letras y/o números).')
    else:
        raise ValidationError('Selecciona un tipo de documento válido.')

    return doc


def validar_correo(correo):    
    correo = (correo or '').strip()
    if not re.match(r'^[^@\s]+@[^@\s]+$', correo):
        raise ValidationError('Ingresa un correo electrónico válido (debe contener @).')
    return correo