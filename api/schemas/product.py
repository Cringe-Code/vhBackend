from api.app import ma
from api.models import Product, ProductAvailability
from .category import CategoryInfoSchema
from .shop import ShortShopSchema
from marshmallow import validate, validates, validates_schema, \
    ValidationError, post_dump

class ProductAvailabilitySchema(ma.SQLAlchemySchema):
    class Meta:
        model = ProductAvailability
        include_fk = True
        ordered = True

    shop = ma.Nested(ShortShopSchema)
    amount = ma.auto_field()

class ReferencedProductSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Product
        include_fk = True

    id = ma.auto_field(dump_only=True)
    title = ma.auto_field(dump_only=True)
    specifications = ma.auto_field(dump_only=True)


class ProductSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Product
        include_fk = True

    id = ma.auto_field(dump_only=True)
    category = ma.Nested(CategoryInfoSchema, dump_only=True)
    title = ma.auto_field(dump_only=True)
    description = ma.auto_field(dump_only=True)
    price = ma.auto_field(dump_only=True)
    referenced_product = ma.Nested(ReferencedProductSchema, dump_only=True, many=True)
    specifications = ma.auto_field(dump_only=True)

    available = ma.Nested(ProductAvailabilitySchema, dump_only=True, many=True)


class ProductCreateSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Product

    title = ma.auto_field(required=True, validate=validate.Length(
        min=1, max=64
    ))
    description = ma.String()
    price = ma.auto_field(required=True)
    parent_fk = ma.auto_field()
    category_fk = ma.auto_field(required=True)
    subcategory_fk = ma.auto_field()
    specifications = ma.auto_field()
    is_child = ma.auto_field(required=True)

