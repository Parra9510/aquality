"""
tests/test_modelos.py
Pruebas unitarias de los modelos y servicios de AQUALITY.
Se ejecutan con: pytest tests/ -v
"""
import pytest
from datetime import date
from unittest.mock import MagicMock, patch

# ── Importaciones de modelos ──────────────────────────────────────────────────
from app.models.usuario    import Usuario, RolUsuario
from app.models.estanque   import Estanque
from app.models.lectura    import LecturaHidrica
from app.models.inventario import Insumo, MovimientoStock, TipoMovimiento
from app.models.personal   import Personal
from app.utils.validaciones import (
    validar_email, validar_cedula,
    validar_rango_numerico, sanitizar_texto,
)


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 1 – Modelo Usuario
# ══════════════════════════════════════════════════════════════════════════════

class TestUsuario:
    """Pruebas unitarias del modelo Usuario."""

    def test_creacion_correcta(self):
        """__init__ crea el usuario con los atributos esperados."""
        u = Usuario(nombre="Ana López", email="ana@acuicultura.co",
                    password="segura123", rol=RolUsuario.SUPERVISOR)
        assert u.nombre == "Ana López"
        assert u.email  == "ana@acuicultura.co"
        assert u.rol    == RolUsuario.SUPERVISOR

    def test_password_no_se_almacena_en_claro(self):
        """La contraseña no debe quedar en texto plano."""
        u = Usuario(nombre="Test", email="t@t.co", password="clave123")
        assert u._password_hash != "clave123"
        assert len(u._password_hash) == 64  # SHA-256 hex

    def test_verificar_password_correcta(self):
        """verificar_password retorna True con la clave correcta."""
        u = Usuario(nombre="Test", email="t@t.co", password="clave123")
        assert u.verificar_password("clave123") is True

    def test_verificar_password_incorrecta(self):
        """verificar_password retorna False con clave incorrecta."""
        u = Usuario(nombre="Test", email="t@t.co", password="clave123")
        assert u.verificar_password("incorrecta") is False

    def test_password_muy_corta_lanza_error(self):
        """Contraseña de menos de 6 caracteres debe lanzar ValueError."""
        with pytest.raises(ValueError, match="6 caracteres"):
            Usuario(nombre="Test", email="t@t.co", password="abc")

    def test_es_administrador(self):
        admin = Usuario(nombre="Admin", email="admin@acuicultura.co",
                        password="admin123", rol=RolUsuario.ADMINISTRADOR)
        assert admin.es_administrador() is True

    def test_no_es_administrador_si_es_operario(self):
        op = Usuario(nombre="Ops", email="ops@acuicultura.co",
                     password="ops12345", rol=RolUsuario.OPERARIO)
        assert op.es_administrador() is False

    def test_str_devuelve_cadena_legible(self):
        u = Usuario(nombre="Pedro", email="p@t.co", password="pedro123",
                    rol=RolUsuario.OPERARIO)
        resultado = str(u)
        assert "Pedro" in resultado
        assert "operario" in resultado

    def test_repr(self):
        u = Usuario(nombre="Pedro", email="p@t.co", password="pedro123")
        assert "Usuario" in repr(u)

    def test_to_dict_contiene_campos_esperados(self):
        u = Usuario(nombre="Ana", email="ana@test.co", password="ana12345")
        d = u.to_dict()
        for campo in ("nombre", "email", "rol"):
            assert campo in d


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 2 – Modelo Estanque
# ══════════════════════════════════════════════════════════════════════════════

class TestEstanque:
    """Pruebas unitarias del modelo Estanque."""

    def test_creacion_correcta(self):
        e = Estanque(codigo="EST-01", nombre="Estanque Norte",
                     capacidad_kg=500.0, volumen_m3=12.0)
        assert e.codigo       == "EST-01"
        assert e.capacidad_kg == 500.0

    def test_capacidad_cero_lanza_error(self):
        with pytest.raises(ValueError):
            Estanque(codigo="EST-00", nombre="Malo", capacidad_kg=0)

    def test_capacidad_negativa_lanza_error(self):
        with pytest.raises(ValueError):
            Estanque(codigo="EST-00", nombre="Malo", capacidad_kg=-100)

    def test_str_contiene_codigo(self):
        e = Estanque(codigo="EST-02", nombre="Sur", capacidad_kg=200)
        assert "EST-02" in str(e)

    def test_to_dict_contiene_campos(self):
        e = Estanque(codigo="EST-03", nombre="Este", capacidad_kg=300)
        d = e.to_dict()
        assert "codigo" in d
        assert "capacidad_kg" in d


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 3 – Modelo LecturaHidrica (con polimorfismo)
# ══════════════════════════════════════════════════════════════════════════════

class TestLecturaHidrica:
    """Pruebas unitarias de LecturaHidrica y su método evaluar() (polimorfismo)."""

    def _lectura_normal(self):
        return LecturaHidrica(
            estanque_id=1, usuario_id=1,
            temperatura=14.0, ph=7.2, oxigeno=9.0
        )

    def _lectura_alerta(self):
        return LecturaHidrica(
            estanque_id=1, usuario_id=1,
            temperatura=25.0,   # fuera de rango (> 18)
            ph=7.0,
            oxigeno=9.0,
        )

    def test_lectura_normal_no_genera_alerta(self):
        l = self._lectura_normal()
        assert l.alerta is False

    def test_lectura_fuera_de_rango_genera_alerta(self):
        l = self._lectura_alerta()
        assert l.alerta is True

    def test_evaluar_temperatura_normal(self):
        l = self._lectura_normal()
        diag = l.evaluar()
        assert diag["temperatura"]["estado"] == "NORMAL"

    def test_evaluar_temperatura_alta(self):
        l = self._lectura_alerta()
        diag = l.evaluar()
        assert diag["temperatura"]["estado"] == "ALTO"

    def test_evaluar_ph_bajo(self):
        l = LecturaHidrica(estanque_id=1, usuario_id=1,
                           temperatura=14.0, ph=5.0, oxigeno=9.0)
        diag = l.evaluar()
        assert diag["ph"]["estado"] == "BAJO"

    def test_temperatura_fisica_invalida(self):
        with pytest.raises(ValueError):
            LecturaHidrica(estanque_id=1, usuario_id=1,
                           temperatura=99.0, ph=7.0, oxigeno=9.0)

    def test_ph_invalido(self):
        with pytest.raises(ValueError):
            LecturaHidrica(estanque_id=1, usuario_id=1,
                           temperatura=14.0, ph=15.0, oxigeno=9.0)

    def test_oxigeno_negativo_invalido(self):
        with pytest.raises(ValueError):
            LecturaHidrica(estanque_id=1, usuario_id=1,
                           temperatura=14.0, ph=7.0, oxigeno=-1.0)

    def test_to_dict_incluye_diagnostico(self):
        l = self._lectura_normal()
        d = l.to_dict()
        assert "diagnostico" in d
        assert "temperatura" in d["diagnostico"]

    def test_str_contiene_temperatura(self):
        l = self._lectura_normal()
        assert "14.0" in str(l)

    def test_alerta_general_en_evaluar(self):
        l = self._lectura_alerta()
        diag = l.evaluar()
        assert diag["alerta_general"] is True


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 4 – Modelo Insumo e inventario
# ══════════════════════════════════════════════════════════════════════════════

class TestInsumo:
    """Pruebas unitarias del modelo Insumo."""

    def test_stock_inicial_es_cero(self):
        i = Insumo(nombre="Alimento pelletizado", unidad_medida="kg")
        assert i.stock_actual == 0.0

    def test_requiere_reabastecimiento_si_stock_bajo(self):
        i = Insumo(nombre="Sal mineral", stock_minimo=20.0)
        i.stock_actual = 5.0
        assert i.requiere_reabastecimiento is True

    def test_no_requiere_reabastecimiento_si_stock_ok(self):
        i = Insumo(nombre="Vitaminas", stock_minimo=10.0)
        i.stock_actual = 50.0
        assert i.requiere_reabastecimiento is False

    def test_str_contiene_nombre(self):
        i = Insumo(nombre="Antibiótico preventivo")
        assert "Antibiótico preventivo" in str(i)

    def test_to_dict_incluye_alerta_stock(self):
        i = Insumo(nombre="Oxígeno líquido")
        d = i.to_dict()
        assert "requiere_reabastecimiento" in d


class TestMovimientoStock:
    """Pruebas unitarias de MovimientoStock."""

    def test_cantidad_negativa_lanza_error(self):
        with pytest.raises(ValueError):
            MovimientoStock(insumo_id=1, usuario_id=1,
                            tipo=TipoMovimiento.ENTRADA, cantidad=-10)

    def test_cantidad_cero_lanza_error(self):
        with pytest.raises(ValueError):
            MovimientoStock(insumo_id=1, usuario_id=1,
                            tipo=TipoMovimiento.SALIDA, cantidad=0)

    def test_creacion_correcta(self):
        m = MovimientoStock(insumo_id=1, usuario_id=1,
                             tipo=TipoMovimiento.ENTRADA, cantidad=50.0,
                             motivo="Compra semanal")
        assert m.cantidad == 50.0
        assert m.tipo     == TipoMovimiento.ENTRADA

    def test_str_entrada_tiene_signo_positivo(self):
        m = MovimientoStock(insumo_id=1, usuario_id=1,
                             tipo=TipoMovimiento.ENTRADA, cantidad=10)
        assert "+" in str(m)


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 5 – Modelo Personal
# ══════════════════════════════════════════════════════════════════════════════

class TestPersonal:
    """Pruebas unitarias del modelo Personal."""

    def _persona(self):
        return Personal(
            cedula="1234567890",
            nombre="Carlos Ruiz",
            cargo="Técnico Acuícola",
            fecha_ingreso=date(2023, 1, 15),
            telefono="3001234567",
        )

    def test_activo_por_defecto(self):
        p = self._persona()
        assert p.activo is True

    def test_desactivar_cambia_estado(self):
        p = self._persona()
        p.desactivar()
        assert p.activo is False

    def test_dias_laborados_es_positivo(self):
        p = self._persona()
        assert p.dias_laborados > 0

    def test_str_contiene_nombre_y_cargo(self):
        p = self._persona()
        texto = str(p)
        assert "Carlos Ruiz" in texto
        assert "Técnico Acuícola" in texto

    def test_to_dict_incluye_dias_laborados(self):
        p = self._persona()
        d = p.to_dict()
        assert "dias_laborados" in d


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 6 – Utilidades de validación
# ══════════════════════════════════════════════════════════════════════════════

class TestValidaciones:
    """Pruebas unitarias de las funciones de validación."""

    def test_email_valido(self):
        assert validar_email("usuario@dominio.com") is True

    def test_email_sin_arroba(self):
        assert validar_email("usuariodominio.com") is False

    def test_email_sin_dominio(self):
        assert validar_email("usuario@") is False

    def test_cedula_valida(self):
        assert validar_cedula("1234567890") is True

    def test_cedula_con_letras(self):
        assert validar_cedula("123abc") is False

    def test_cedula_muy_corta(self):
        assert validar_cedula("123") is False

    def test_rango_numerico_correcto(self):
        assert validar_rango_numerico(7.0, 0, 14, "ph") == 7.0

    def test_rango_numerico_fuera_de_rango(self):
        with pytest.raises(ValueError):
            validar_rango_numerico(15.0, 0, 14, "ph")

    def test_rango_numerico_no_numerico(self):
        with pytest.raises(ValueError):
            validar_rango_numerico("abc", 0, 14, "ph")

    def test_sanitizar_texto_elimina_espacios(self):
        assert sanitizar_texto("  hola  ") == "hola"

    def test_sanitizar_texto_trunca(self):
        largo = "x" * 300
        assert len(sanitizar_texto(largo, max_len=200)) == 200


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 7 – Servicio ClimaService (mock de API externa)
# ══════════════════════════════════════════════════════════════════════════════

class TestClimaService:
    """Pruebas con mock del servicio de API externa."""

    def test_procesar_respuesta_correcta(self):
        from app.services.clima_service import ClimaService
        datos = {
            "current": {
                "temperature_2m":        18.5,
                "relative_humidity_2m":  75,
                "precipitation":         0.0,
                "wind_speed_10m":        5.2,
                "time":                  "2025-05-08T12:00",
            },
            "timezone": "America/Bogota",
        }
        resultado = ClimaService._procesar_respuesta(datos)
        assert resultado["temperatura_ambiente_c"] == 18.5
        assert resultado["humedad_relativa_pct"]   == 75

    def test_procesar_respuesta_sin_current_lanza_error(self):
        from app.services.clima_service import ClimaService, ClimaAPIError
        with pytest.raises(ClimaAPIError):
            ClimaService._procesar_respuesta({"sin_campo": True})

    def test_obtener_clima_actual_mock(self):
        """Prueba la llamada HTTP con requests mockeado."""
        from app.services.clima_service import ClimaService
        respuesta_mock = MagicMock()
        respuesta_mock.raise_for_status = MagicMock()
        respuesta_mock.json.return_value = {
            "current": {
                "temperature_2m": 20.0,
                "relative_humidity_2m": 80,
                "precipitation": 0.0,
                "wind_speed_10m": 3.0,
                "time": "2025-05-08T14:00",
            },
            "timezone": "America/Bogota",
        }
        with patch("app.services.clima_service.requests.get",
                   return_value=respuesta_mock) as mock_get:
            svc = ClimaService()
            resultado = svc.obtener_clima_actual()
            mock_get.assert_called_once()
            assert resultado["temperatura_ambiente_c"] == 20.0

    def test_estimar_temperatura_agua(self):
        """La temperatura del agua estimada es ≈ 85% de la ambiente."""
        from app.services.clima_service import ClimaService
        svc = ClimaService()
        with patch.object(svc, "obtener_clima_actual",
                          return_value={"temperatura_ambiente_c": 20.0}):
            estimada = svc.estimar_temperatura_agua()
            assert estimada == pytest.approx(17.0, abs=0.1)
