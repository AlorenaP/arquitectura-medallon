#!/bin/bash
set -e

echo "[entrypoint] Ejecutando ingesta inicial..."
python ingesta_inicial.py

echo "[entrypoint] Iniciando ingesta continua..."
exec python ingesta_continua.py
