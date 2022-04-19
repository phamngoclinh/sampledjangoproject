function Order ({ amount_total = 0, amount_price = 0, amount_sub_total = 0, orderdetails = [] }) {
  this.amount_total = parseInt(amount_total)
  this.amount_sub_total = parseInt(amount_sub_total)
  this.amount_price = parseInt(amount_price)
  this.orderdetails = orderdetails

  this.compute = function () {
    let amount_sub_total = 0, amount_price = 0
    this.orderdetails.forEach(function (orderdetail) {
      amount_sub_total += orderdetail.sub_total
      amount_price += (orderdetail.price_unit * orderdetail.quantity)
    })
    this.amount_total = amount_sub_total
    this.amount_price = amount_price
    this.amount_sub_total = amount_sub_total
  }

  /**
   * Processing for the following cases:
   * Add new a cart item
   * Set quantity of a cart tiem
   * Remove cart item
   * @param {productModel} product require
   * @param {number} quantity optional
   */
  this.addProduct = function (product, quantity) {
    if (!(product instanceof Product))
      throw new Error('Order.addProduct require a instance of Product')

    const orderdetail = this.orderdetails.find(function (orderdetail) {
      return orderdetail.product.id === product.id
    })
    if (orderdetail) {
      if (quantity > 0) // Increase, decrease quantity in cart item
        orderdetail.setQuantity(quantity)
      else if (quantity === 0)
        this.orderdetails = this.orderdetails.filter(function (orderdetail) { // Remove cart item
          return orderdetail.product.id !== product.id
        })
      else
        orderdetail.setQuantity(orderdetail.quantity + 1) // Add more 1 unit of quantity
    } else {
      this.orderdetails.push(new OrderDetail({ product })) // Add new a cart item
    }
  }

  this.getOrderDetail = function (productId) {
    return this.orderdetails.find(function (orderdetail) { return orderdetail.product.id === productId })
  }
}

function OrderDetail ({ product, quantity = 1 }) {
  if (!product) throw new Error('OrderDetail.constructor require a instance of Product for key \'product\'')

  this.product = product
  this.quantity = parseInt(quantity)
  this.sub_price_unit = product.sub_price
  this.price_unit = product.price
  this.amount_price = product.price * parseInt(quantity)
  this.sub_total = product.sub_price
                    ? product.sub_price * quantity
                    : product.price * quantity

  this.setQuantity = function (quantity) {
    this.quantity = parseInt(quantity)
    this.computeSubTotal()
  }

  this.computeSubTotal = function () {
    this.sub_total = this.sub_price_unit
                      ? this.sub_price_unit * this.quantity
                      : this.price_unit * this.quantity
    this.amount_price = this.quantity * this.price_unit
  }
}

function Product ({ id, name, slug, image, price, url = '', sub_price = 0 }) {
  this.id = id
  this.name = name
  this.slug = slug
  this.image = image
  this.price = parseInt(price)
  this.sub_price = parseInt(sub_price)
  this.url = url
}

const CART_DATA = function () {
  const data = localStorage.getItem('CART_DATA')
  if (!data) { return { order: new Order({}) } }
  dataJson = JSON.parse(data)

  // Mapping dataJson into dataModel
  const dataModel = { order: new Order({}) }
  if (dataJson.order && dataJson.order.orderdetails && dataJson.order.orderdetails.length) {
    const orderdetails = []
    dataJson.order.orderdetails.forEach(function (orderdetail) {
      const productModel = new Product(orderdetail.product)
      const orderdetailModel = new OrderDetail({ product: productModel, quantity: orderdetail.quantity })
      orderdetails.push(orderdetailModel)
    })
    const orderModel = new Order({
      amount_total: dataJson.order.amount_total,
      amount_sub_total: dataJson.order.amount_sub_total,
      amount_price: dataJson.order.amount_price,
      orderdetails
    })
    dataModel.order = orderModel
  }

  return dataModel
}()

$(document).ready(function () {
  // Cart top
  $('.cart-sum-item').html(CART_DATA.order.orderdetails.length)
  $('.cart-amount-price').html(CART_DATA.order.amount_price.toLocaleString() + 'đ')
  $('.cart-amount-sub-total').html(CART_DATA.order.amount_sub_total.toLocaleString() + 'đ')
  $('.cart-amount-total').html(CART_DATA.order.amount_total.toLocaleString() + 'đ')

  // Cart
  $.each(CART_DATA.order.orderdetails, function (index, orderdetail) {
    let price = `<strong class="currency">${(orderdetail.price_unit * orderdetail.quantity).toLocaleString()}đ</strong>`
    if (orderdetail.sub_price_unit) {
      price = `
        <strong class="currency">${(orderdetail.sub_price_unit * orderdetail.quantity).toLocaleString()}đ</strong>
        <span class="price-discount currency">${(orderdetail.price_unit * orderdetail.quantity).toLocaleString()}₫</span>
      `
    }
    $('.cart-list').prepend(`
      <div
        class="cart-item item"
        data-orderdetail-id="${orderdetail.id}"
        data-orderdetail-quantity="${orderdetail.quantity}"
        data-product-id="${orderdetail.product.id}"
        data-product-price="${orderdetail.product.price}"
        data-product-discount-price="${orderdetail.product.sub_price}"
      >
        <img alt="${orderdetail.product.name}" src="${orderdetail.product.image}" width="60" height="60">
        <div class="colinfo">
          <a href="${orderdetail.product.url}" class="name">${orderdetail.product.name}</a>
          <div class="quantity">
            <div class="quantitynum">
              <i class="noselect">-</i>
              <input autocomplete="off" type="number" min="1" max="50" class="qty" value="${orderdetail.quantity}">
              <i class="noselect">+</i>
            </div>
            <a class="delete">Xóa</a>
          </div>
          <div class="npromotion"></div>
        </div>
        <div class="colmoney">${price}</div>
      </div>
    `)
  })

  $('.buy').on('click', function (e) {
    const $product = $(this).closest('.product-item')
    if ($product) {
      const product = new Product({
        id: $product.data('product-id'),
        name: $product.data('product-name'),
        slug: $product.data('product-slug'),
        image: $product.data('product-image'),
        price: $product.data('product-price'),
        sub_price: $product.data('product-discount-price'),
        url: $product.data('product-url'),
      })
      CART_DATA.order.addProduct(product)
      CART_DATA.order.compute()
      localStorage.setItem('CART_DATA', JSON.stringify(CART_DATA))

      $('.cart-sum-item').html(CART_DATA.order.orderdetails.length)
      $('.cart-amount-price').html(CART_DATA.order.amount_price.toLocaleString() + 'đ')
      $('.cart-amount-sub-total').html(CART_DATA.order.amount_sub_total.toLocaleString() + 'đ')
      $('.cart-amount-total').html(CART_DATA.order.amount_total.toLocaleString() + 'đ')
    }
  })

  $('.cart-item .delete').on('click', function () {
    const $cartItem = $(this).closest('.cart-item')
    const productId = $cartItem.data('product-id')

    const product = new Product({ id: productId })
    CART_DATA.order.addProduct(product, 0)
    CART_DATA.order.compute()
    localStorage.setItem('CART_DATA', JSON.stringify(CART_DATA))

    $cartItem.remove()
    $('.cart-sum-item').html(CART_DATA.order.orderdetails.length)
    $('.cart-amount-price').html(CART_DATA.order.amount_price.toLocaleString() + 'đ')
    $('.cart-amount-sub-total').html(CART_DATA.order.amount_sub_total.toLocaleString() + 'đ')
    $('.cart-amount-total').html(CART_DATA.order.amount_total.toLocaleString() + 'đ')
  })

  $('.cart-item .quantity .qty').on('change', function () {
    const $cartItem = $(this).closest('.cart-item')
    const productId = parseInt($cartItem.data('product-id'))
    const quantity = parseInt($(this).val())

    const product = new Product({ id: productId })
    CART_DATA.order.addProduct(product, quantity)
    CART_DATA.order.compute()
    localStorage.setItem('CART_DATA', JSON.stringify(CART_DATA))

    let orderdetail = CART_DATA.order.getOrderDetail(productId)
    let quantity_sub_price_unit = orderdetail.sub_price_unit * orderdetail.quantity
    let quantity_price = orderdetail.price_unit * orderdetail.quantity
    if (quantity_sub_price_unit) {
      $cartItem.find('.colmoney strong').html(quantity_sub_price_unit.toLocaleString()+'₫')
      $cartItem.find('.colmoney span').html(quantity_price.toLocaleString()+'₫')
    } else {
      $cartItem.find('.colmoney strong').html(quantity_price.toLocaleString()+'₫')
    }

    $('.cart-sum-item').html(CART_DATA.order.orderdetails.length)
    $('.cart-amount-price').html(CART_DATA.order.amount_price.toLocaleString() + 'đ')
    $('.cart-amount-sub-total').html(CART_DATA.order.amount_sub_total.toLocaleString() + 'đ')
    $('.cart-amount-total').html(CART_DATA.order.amount_total.toLocaleString() + 'đ')
  })

  $('.quantitynum i:first-child').on('click', function () {
    const $input = $(this).parent().find('.qty')
    const min = parseInt($input.attr('min'))
    const current = parseInt($input.val())
    if (current > min) {
      $input.val(current - 1)
      $input.trigger('change')
    }
  })

  $('.quantitynum i:last-child').on('click', function () {
    const $input = $(this).parent().find('.qty')
    const max = parseInt($input.attr('max'))
    const current = parseInt($input.val())
    if ($input.val() < max) {
      $input.val(current + 1)
      $input.trigger('change')
    }
  })
})