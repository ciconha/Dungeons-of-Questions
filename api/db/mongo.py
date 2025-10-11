# api/db/mongo.py

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from typing import Any, Dict, List, Optional
from uuid import uuid4

class MongoConnector:
    """
    Gerencia conexão, CRUD básico e conversão de ObjectId.
    """

    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client: Optional[MongoClient] = None
        self.db = None

    def connect(self) -> bool:
        """
        Abre conexão com o MongoDB e testa com ping.
        """
        try:
            self.client = MongoClient(self.uri)
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            print(f"✅ MongoDB conectado em {self.uri}/{self.db_name}")
            return True
        except PyMongoError as e:
            print(f"❌ Erro ao conectar no MongoDB: {e}")
            return False

    def disconnect(self) -> None:
        """
        Fecha a conexão com o MongoDB.
        """
        if self.client:
            self.client.close()
            print("🔌 MongoDB desconectado")

    def insert(self,
               collection: str,
               data: Dict[str, Any],
               *,
               use_uuid: bool = False
    ) -> Dict[str, Any]:
        """
        Insere um documento. Se use_uuid=True, gera _id string via uuid4.
        Retorna {'success': bool, 'id': str | None, 'error': str | None}.
        """
        if use_uuid:
            data["_id"] = uuid4().hex

        try:
            result = self.db[collection].insert_one(data)
            oid = result.inserted_id
            return {
                "success": True,
                "id": str(oid) if isinstance(oid, ObjectId) else oid
            }
        except PyMongoError as e:
            return {"success": False, "id": None, "error": str(e)}

    def find(self,
             collection: str,
             query: Dict[str, Any] = {}
    ) -> Dict[str, Any]:
        """
        Busca múltiplos documentos. Converte ObjectId para str.
        Retorna {'success': bool, 'data': List[Dict], 'error': str | None}.
        """
        try:
            cursor = self.db[collection].find(query)
            docs: List[Dict[str, Any]] = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                docs.append(doc)
            return {"success": True, "data": docs}
        except PyMongoError as e:
            return {"success": False, "data": [], "error": str(e)}

    def find_one(self,
                 collection: str,
                 query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Busca um único documento. Converte ObjectId para str.
        Retorna {'success': bool, 'data': Dict | None, 'error': str | None}.
        """
        try:
            doc = self.db[collection].find_one(query)
            if doc:
                doc["_id"] = str(doc["_id"])
            return {"success": True, "data": doc}
        except PyMongoError as e:
            return {"success": False, "data": None, "error": str(e)}

    def update(self,
               collection: str,
               query: Dict[str, Any],
               update_data: Dict[str, Any],
               *,
               upsert: bool = False
    ) -> Dict[str, Any]:
        """
        Atualiza um documento com $set. upsert opcional.
        Retorna {'success': bool, 'matched_count': int, 'modified_count': int, 'error': str | None}.
        """
        try:
            result = self.db[collection].update_one(
                query, {"$set": update_data}, upsert=upsert
            )
            return {
                "success": True,
                "matched_count": result.matched_count,
                "modified_count": result.modified_count
            }
        except PyMongoError as e:
            return {"success": False, "matched_count": 0, "modified_count": 0, "error": str(e)}

    def delete(self,
               collection: str,
               query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deleta um único documento.
        Retorna {'success': bool, 'deleted_count': int, 'error': str | None}.
        """
        try:
            result = self.db[collection].delete_one(query)
            return {"success": True, "deleted_count": result.deleted_count}
        except PyMongoError as e:
            return {"success": False, "deleted_count": 0, "error": str(e)}


# Instância global
mongo = MongoConnector("mongodb://localhost:27017", "rpg_emily")
