__copyright__ = "Copyright 2021, 3Liz"
__license__ = "GPL version 3"
__email__ = "info@3liz.org"

from typing import Tuple, Union

from qgis.core import (
    QgsAbstractDatabaseProviderConnection,
    QgsDataSourceUri,
    QgsProcessingContext,
    QgsVectorLayer,
)

from openads.processing.base import BaseProcessingAlgorithm


class BaseDataAlgorithm(BaseProcessingAlgorithm):

    OUTPUT = None

    def group(self):
        return "Import des données"

    def groupId(self):
        return "data"

    def init_layer(
        self,
        context: QgsProcessingContext,
        uri: QgsDataSourceUri,
        schema: str,
        table: str,
        geom: str,
        sql: str,
        pk: str = None,
    ) -> Union[QgsVectorLayer, bool]:
        """Create vector layer from database table"""
        if pk:
            uri.setDataSource(schema, table, geom, sql, pk)
        else:
            uri.setDataSource(schema, table, geom, sql)
        layer = QgsVectorLayer(uri.uri(), table, "postgres")
        if not layer.isValid():
            return False
        context.temporaryLayerStore().addMapLayer(layer)
        context.addLayerToLoadOnCompletion(
            layer.id(),
            QgsProcessingContext.LayerDetails(table, context.project(), self.OUTPUT),
        )
        return layer

    layers_name = dict()
    layers_name["communes"] = dict()
    layers_name["communes"]["id"] = "id_communes"
    layers_name["communes"]["geom"] = "geom"
    layers_name["parcelles"] = dict()
    layers_name["parcelles"]["id"] = "id_parcelles"
    layers_name["parcelles"]["geom"] = "geom"
    layers_name["dossiers_openads"] = dict()
    layers_name["dossiers_openads"]["id"] = "id_dossiers_openads"
    layers_name["dossiers_openads"]["geom"] = "geom"
    layers_name["contraintes"] = dict()
    layers_name["contraintes"]["id"] = "id_contraintes"
    layers_name["contraintes"]["geom"] = None

    @staticmethod
    def get_uri(
        connection: QgsAbstractDatabaseProviderConnection,
    ) -> Tuple[str, QgsDataSourceUri]:
        """Function to get uri"""
        uri = QgsDataSourceUri(connection.uri())
        is_host = uri.host() != ""
        if is_host:
            msg = "Connexion établie via l'hôte"
        else:
            msg = "Connexion établie via le service"
        return msg, uri

    def import_layer(
        self,
        context: QgsProcessingContext,
        uri: QgsDataSourceUri,
        schema: str,
        name: str,
    ) -> Union[Tuple[str, QgsVectorLayer], Tuple[str, bool]]:
        """Function to import layer"""
        if context.project().mapLayersByName(name):
            return f"La couche {name} est déjà présente", False

        result = self.init_layer(
            context,
            uri,
            schema,
            name,
            self.layers_name[name]["geom"],
            "",
            self.layers_name[name]["id"],
        )
        if not result:
            return f"La couche {name} ne peut pas être chargée", False
        else:
            return f"La couche {name} a pu être chargée", result
