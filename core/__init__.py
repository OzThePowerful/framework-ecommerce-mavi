"""Infraestructura transversal del Framework Ecommerce MAVI.

Regla de dependencia: `core` nunca importa `pages`, `workflows` ni `tests`.
Los módulos funcionales dependen de `core`, nunca al contrario.
"""
