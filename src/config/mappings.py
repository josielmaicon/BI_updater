FILE_DESTINATION_MAP = {
    "documentSAC": "Indicadores/Documentos",
    "paradas": "Indicadores/Paradas",
    "fretes": "Indicadores/Fretes"
}

COMPROVEI_EXPORTS = {
    "paradas": {
        "url": "https://api.comprovei.com.br/api/1.1/util/export/documentStop",
        "auth": "basic"
    },
    "documentos": {
        "url": "https://console-api.comprovei.com/exports/documentSAC",
        "auth": "basic"
    },
    "rotas": {
        "url": "https://api.comprovei.com.br/api/1.1/util/export/route",
        "auth": "basic"
    }
}

FILE_CLASSIFICATION_RULES = [
    {
        "match": "documentos",
        "tipo": "documentos",
        "sharepoint_path": "Power BI/Base de Dados/Operacional/Documentos/Atual",
        "powerbi_dataset": "bi_documentos",
        "comprovei_tipo": "documentos" 
    },
    {
        "match": "paradas",
        "tipo": "paradas",
        "sharepoint_path": "Power BI/Base de Dados/Operacional/Paradas/Atual",
        "powerbi_dataset": "bi_paradas",
        "comprovei_tipo": "paradas" 
    },
    {
        "match": "rotas",
        "tipo": "rotas",
        "sharepoint_path": "Power BI/Base de Dados/Operacional/Rotas/Atual",
        "powerbi_dataset": "bi_rotas",
        "comprovei_tipo": "rotas" 
    }
]
