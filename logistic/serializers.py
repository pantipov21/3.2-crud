from rest_framework import serializers
from .models import Product, Stock, StockProduct

class ProductSerializer(serializers.ModelSerializer):
	# настройте сериализатор для продукта
	class Meta:
		model = Product
		fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
# настройте сериализатор для позиции продукта на складе
	class Meta:
		model = StockProduct
		fields = ['product', 'quantity', 'price']

    
    
class StockSerializer(serializers.ModelSerializer):
	positions = ProductPositionSerializer(many=True)
	
	# настройте сериализатор для склада
	class Meta:
		model = Stock
		fields = ['address', 'positions']

	def create(self, validated_data):
		# достаем связанные данные для других таблиц
		positions = validated_data.pop('positions')


		# создаем склад по его параметрам
		stock = super().create(validated_data)

		# здесь вам надо заполнить связанные таблицы
		# в нашем случае: таблицу StockProduct
		# с помощью списка positions
		for el in positions:
			StockProduct.objects.create(stock=stock, **el)
		return stock

	def update(self, instance, validated_data):
		# достаем связанные данные для других таблиц
		positions = validated_data.pop('positions')

		# обновляем склад по его параметрам
		stock = super().update(instance, validated_data)

		# здесь вам надо обновить связанные таблицы
		# в нашем случае: таблицу StockProduct
		# с помощью списка positions
		positions_instance = instance.positions.all()

		for r in positions_instance:
			for w in positions:
				if r.product == w['product']:
					if 'price' in w:
						r.price = w['price']
					if 'quantity' in w:
						r.quantity = w['quantity']
					if r.product.id != w['product'].id:
						StockProduct.objects.create(product=w['product'], price=w['price'],quantity=w['quantity'],stock_id=r.stock_id)
						r.save()

		return stock
