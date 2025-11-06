from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, obj_id, data):
        pass

    @abstractmethod
    def delete(self, obj_id):
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        pass


class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}

    def add(self, obj):
        self._storage[obj.id] = obj

    def get(self, obj_id):
        return self._storage.get(obj_id)

    def get_all(self):
        return list(self._storage.values())

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj:
            obj.update(data)

    def delete(self, obj_id):
        if obj_id in self._storage:
            del self._storage[obj_id]

    def get_by_attribute(self, attr_name, attr_value):
        return next((obj for obj in self._storage.values() if getattr(obj, attr_name) == attr_value), None)

class SQLAlchemyRepository(Repository):
    """Repository utilisant SQLAlchemy pour la persistence en base de données"""
    
    def __init__(self, model):
        """
        Initialise le repository avec un modèle SQLAlchemy
        
        Args:
            model: La classe du modèle SQLAlchemy (ex: User, Place, Review)
        """
        self.model = model

    def add(self, obj):
        """Ajoute un objet à la base de données"""
        from app.extensions import db
        db.session.add(obj)
        db.session.commit()

    def get(self, obj_id):
        """Récupère un objet par son ID"""
        return self.model.query.get(obj_id)

    def get_all(self):
        """Récupère tous les objets"""
        return self.model.query.all()

    def update(self, obj_id, data):
        """Met à jour un objet existant"""
        from app.extensions import db
        obj = self.get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            db.session.commit()

    def delete(self, obj_id):
        """Supprime un objet de la base de données"""
        from app.extensions import db
        obj = self.get(obj_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()

    def get_by_attribute(self, attr_name, attr_value):
        """Récupère un objet par un attribut spécifique"""
        return self.model.query.filter_by(**{attr_name: attr_value}).first()