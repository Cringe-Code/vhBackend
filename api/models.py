import enum
from datetime import datetime, timedelta
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Float, DateTime, Boolean, JSON, Enum
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from api.app import db


class Updatable:
    def update(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)


class OrderStatus(enum.Enum):
    awaiting_payment = 0
    forming = 1
    waiting_to_receive = 2
    in_delivery = 3
    finished = 4
    canceled_by_system = 5
    canceled_by_user = 6


class DeliveryType(enum.Enum):
    pickup = 0
    delivery = 1


class PaymentType(enum.Enum):
    prepay = 0
    postpayment = 1


class ObjectStorage(db.Model):
    __tablename__ = 'ObjectStorage'

    id = Column(Integer, primary_key=True)
    link = Column(String(1024), index=True)

    product = relationship('Product', back_populates='image')


class User(Updatable, db.Model):
    __tablename__ = 'Users'

    # Основная информация
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), index=True, unique=True, nullable=False)
    password = Column(String(128))
    role_fk = Column(Integer, ForeignKey('UserRole.id'))

    # Личная информация
    firstName = Column(String(64))
    lastName = Column(String(64), index=True)
    birthday = Column(DateTime)

    # Адрес доставки
    city = Column(String(128))
    street = Column(String(128))
    building = Column(String(64))
    flat = Column(String(32))
    zipcode = Column(Integer)

    # Системная информация
    notificationsAgree = Column(Boolean, default=True)
    registrationDate = Column(DateTime, default=datetime.utcnow)

    role = relationship('UserRole', back_populates='users')
    reserved = relationship('ProductReserve', back_populates='user')
    likes = relationship('Favourite', back_populates='user')
    basket = relationship('Basket', back_populates='user')

    def check_password(self, password) -> bool:
        return check_password_hash(self.password, password)

    def update_password(self, new_password, old_password) -> bool:
        if check_password_hash(self.password, old_password):
            self.password = generate_password_hash(new_password)
            db.session.add(self)
            db.session.commit()
            return True
        else:
            return False



class Shop(db.Model):
    __tablename__ = 'Shop'

    id = Column(Integer, primary_key=True)
    title = Column(String(64), nullable=False)

    city = Column(String(128))
    street = Column(String(128))
    building = Column(String(64))
    description = Column(String(512))
    preview = Column(String(1024))

    available = relationship('ProductAvailability', back_populates='product')
    orders = relationship('Order', back_populates='shop')


class UserRole(db.Model):
    __tablename__ = 'UserRole'

    id = Column(Integer, primary_key=True)
    roleName = Column(String(64), unique=True, nullable=False)
    roleDescription = Column(String(128))

    users = relationship('User', back_populates='role')
    rights = relationship('UserRoleRights', back_populates='role')

    def get_rights(self):
        return [i.right for i in self.rights]


class UserRoleRights(db.Model):
    __tablename__ = 'UserRoleRights'

    id = Column(Integer, primary_key=True)
    role_fk = Column(Integer, ForeignKey('UserRole.id', ondelete='CASCADE'))
    right = Column(String(128), nullable=False)

    role = relationship('UserRole', back_populates='rights')


class Category(db.Model):
    __tablename__ = 'Category'

    id = Column(Integer, primary_key=True)
    title = Column(String(64), index=True)
    not_for_children = Column(Boolean, nullable=False, default=False)

    subcategories = relationship('SubCategory', back_populates='categories')
    products = relationship('Product', back_populates='categories')


class SubCategory(db.Model):
    __tablename__ = 'SubCategory'

    id = Column(Integer, primary_key=True)
    title = Column(String(64), index=True)
    category_fk = Column(Integer, ForeignKey('Category.id', ondelete='CASCADE'))

    categories = relationship('Category', back_populates='subcategories')
    products = relationship('Product', back_populates='subcategory')


class Product(db.Model):
    __tablename__ = 'Product'

    id = Column(Integer, primary_key=True)
    title = Column(String(128), index=True, nullable=False)
    description = Column(String(1024), index=True)
    image_fk = Column(Integer, ForeignKey('ObjectStorage.id'))
    price = Column(Float(2), nullable=False, index=True)
    is_child = Column(Boolean, nullable=False)

    parent_fk = Column(Integer, ForeignKey('Product.id'), nullable=True)
    category_fk = Column(Integer, ForeignKey('Category.id'), nullable=False)
    subcategory_fk = Column(Integer, ForeignKey('SubCategory.id', ondelete='CASCADE'))

    specifications = Column(JSON, default=None)

    # referenced_product = relationship('Product', back_populates='referenced_product')
    referenced_product = relationship('Product')
    category = relationship('Category', back_populates='product')
    subcategory = relationship('SubCategory', back_populates='product')
    available = relationship('ProductAvailability', back_populates='product')
    reserved = relationship('ProductReserve', back_populates='product')
    liked = relationship('Favourite', back_populates='product')
    in_baskets = relationship('Basket', back_populates='product')
    image = relationship('ObjectStorage', back_populates='product')


class ProductAvailability(db.Model):
    __tablename__ = 'ProductAvailability'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('Product.id'))
    shop_id = Column(Integer, ForeignKey('Shop.id'))
    amount = Column(Integer, nullable=False, default=0)

    product = relationship('Product', back_populates='available')
    shop = relationship('Shop', back_populates='available')
    reserved = relationship('ProductReserve', back_populates='pa')


class ProductReserve(db.Model):
    __tablename__ = 'ProductReserve'

    id = Column(Integer, primary_key=True)
    user_fk = Column(Integer, ForeignKey('User.id'))
    product_fk = Column(Integer, ForeignKey('Product.id', ondelete='CASCADE'))
    pa_fk = Column(Integer, ForeignKey('ProductAvailability.id', ondelete='CASCADE')) # ProductAvailability_FK
    # order = Column(Integer, ForeignKey('Order.id')) TODO: add Order
    amount = Column(Integer, nullable=False)

    user = relationship('User', back_populates='reserved')
    product = relationship('Product', back_populates='reserved')
    pa = relationship('ProductAvailability', back_populates='reserved')
    # order = relationship('Order', back_populates='reserved')


class Favourite(db.Model):
    __tablename__ = 'Favourite'

    id = Column(Integer, primary_key=True)
    user_fk = Column(Integer, ForeignKey('User.id'))
    product_fk = Column(Integer, ForeignKey('Product.id'), index=True)

    user = relationship('User', back_populates='likes')
    product = relationship('Product', back_populates='liked')


class Basket(db.Model):
    __tablename__ = 'Basket'

    id = Column(Integer, primary_key=True)
    user_fk = Column(Integer, ForeignKey('User.id'), nullable=False, index=True)
    product_fk = Column(Integer, ForeignKey('Product.id'), nullable=False)
    amount = Column(Integer, nullable=False, default=1)

    user = relationship('User', back_populates='basket')
    product = relationship('Product', back_populates='in_baskets')


class Order(db.Model):
    __tablename__ = 'Order'

    id = Column(Integer, primary_key=True)
    user_fk = Column(Integer, ForeignKey('User.id'), nullable=False, index=True)
    status = Column(Enum(OrderStatus), nullable=False)
    delivery_type = Column(Enum(DeliveryType), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    sum = Column(Float(2), nullable=False)
    # TODO: Used promocodes
    # TODO: Used promo
    shop_fk = Column(Integer, ForeignKey('Shop.id'), index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    shop = relationship('Shop', back_populates='orders')


class OrderItem(db.Model):
    __tablename__ = 'OrderItem'

    id = Column(Integer, primary_key=True)
    product_fk = Column(Integer, ForeignKey('Product.id'), nullable=False)
    price = Column(Float(2), nullable=False)
    amount = Column(Integer, nullable=False)

#     TODO: Заказы, Настройки, Отзывы, Акции, Скидочные карты, Промокоды


