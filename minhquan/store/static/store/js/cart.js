function POS ({ amount_total = 0, amount_price = 0, amount_sub_total = 0, posdetails = [] }) {
  this.amount_total = parseInt(amount_total)
  this.amount_sub_total = parseInt(amount_sub_total)
  this.amount_price = parseInt(amount_price)
  this.posdetails = posdetails

  this.compute = function () {
    let amount_sub_total = 0, amount_price = 0
    this.posdetails.forEach(function (posdetail) {
      amount_sub_total += posdetail.sub_total
      amount_price += (posdetail.price_unit * posdetail.quantity)
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
      throw new Error('POS.addProduct require a instance of Product')

    const posdetail = this.posdetails.find(function (posdetail) {
      return posdetail.product.id === product.id
    })
    if (posdetail) {
      if (quantity > 0) // Increase, decrease quantity in cart item
        posdetail.setQuantity(quantity)
      else if (quantity === 0)
        this.posdetails = this.posdetails.filter(function (posdetail) { // Remove cart item
          return posdetail.product.id !== product.id
        })
      else
        posdetail.setQuantity(posdetail.quantity + 1) // Add more 1 unit of quantity
    } else {
      this.posdetails.push(new POSDetail({ product })) // Add new a cart item
    }
  }

  this.getPOSDetail = function (productId) {
    return this.posdetails.find(function (posdetail) { return posdetail.product.id === productId })
  }
}

function POSDetail ({ product, quantity = 1 }) {
  if (!product) throw new Error('POSDetail.constructor require a instance of Product for key \'product\'')

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
  if (!data) { return { pos: new POS({}) } }
  dataJson = JSON.parse(data)

  // Mapping dataJson into dataModel
  const dataModel = { pos: new POS({}) }
  if (dataJson.pos && dataJson.pos.posdetails && dataJson.pos.posdetails.length) {
    const posdetails = []
    dataJson.pos.posdetails.forEach(function (posdetail) {
      const productModel = new Product(posdetail.product)
      const posdetailModel = new POSDetail({ product: productModel, quantity: posdetail.quantity })
      posdetails.push(posdetailModel)
    })
    const posModel = new POS({
      amount_total: dataJson.pos.amount_total,
      amount_sub_total: dataJson.pos.amount_sub_total,
      amount_price: dataJson.pos.amount_price,
      posdetails
    })
    dataModel.pos = posModel
  }

  return dataModel
}()

$(document).ready(function () {
  // Cart top
  $('.pos-detail-count').html(CART_DATA.pos.posdetails.length)
  $('.pos-amount-price').html(CART_DATA.pos.amount_price.toLocaleString() + 'đ')
  $('.pos-amount-sub-total').html(CART_DATA.pos.amount_sub_total.toLocaleString() + 'đ')
  $('.pos-amount-total').html(CART_DATA.pos.amount_total.toLocaleString() + 'đ')

  // Cart
  $.each(CART_DATA.pos.posdetails, function (index, posdetail) {
    let price = `<strong class="currency">${(posdetail.price_unit * posdetail.quantity).toLocaleString()}đ</strong>`
    if (posdetail.sub_price_unit) {
      price = `
        <strong class="currency">${(posdetail.sub_price_unit * posdetail.quantity).toLocaleString()}đ</strong>
        <span class="price-discount currency">${(posdetail.price_unit * posdetail.quantity).toLocaleString()}₫</span>
      `
    }
    $('.cart-list').prepend(`
      <div
        class="cart-item item"
        data-posdetail-id="${posdetail.id}"
        data-posdetail-quantity="${posdetail.quantity}"
        data-product-id="${posdetail.product.id}"
        data-product-price="${posdetail.product.price}"
        data-product-discount-price="${posdetail.product.sub_price}"
      >
        <img alt="${posdetail.product.name}" src="${posdetail.product.image}" width="60" height="60">
        <div class="colinfo">
          <a href="${posdetail.product.url}" class="name">${posdetail.product.name}</a>
          <div class="quantity">
            <div class="quantitynum">
              <i class="noselect">-</i>
              <input autocomplete="off" type="number" min="1" max="50" class="qty" value="${posdetail.quantity}">
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
      CART_DATA.pos.addProduct(product)
      CART_DATA.pos.compute()
      localStorage.setItem('CART_DATA', JSON.stringify(CART_DATA))

      $('.pos-detail-count').html(CART_DATA.pos.posdetails.length)
      $('.pos-amount-price').html(CART_DATA.pos.amount_price.toLocaleString() + 'đ')
      $('.pos-amount-sub-total').html(CART_DATA.pos.amount_sub_total.toLocaleString() + 'đ')
      $('.pos-amount-total').html(CART_DATA.pos.amount_total.toLocaleString() + 'đ')
    }
  })

  $('.cart-item .delete').on('click', function () {
    const $cartItem = $(this).closest('.cart-item')
    const productId = $cartItem.data('product-id')

    const product = new Product({ id: productId })
    CART_DATA.pos.addProduct(product, 0)
    CART_DATA.pos.compute()
    localStorage.setItem('CART_DATA', JSON.stringify(CART_DATA))

    $cartItem.remove()
    $('.pos-detail-count').html(CART_DATA.pos.posdetails.length)
    $('.pos-amount-price').html(CART_DATA.pos.amount_price.toLocaleString() + 'đ')
    $('.pos-amount-sub-total').html(CART_DATA.pos.amount_sub_total.toLocaleString() + 'đ')
    $('.pos-amount-total').html(CART_DATA.pos.amount_total.toLocaleString() + 'đ')
  })

  $('.cart-item .quantity .qty').on('change', function () {
    const $cartItem = $(this).closest('.cart-item')
    const productId = parseInt($cartItem.data('product-id'))
    const quantity = parseInt($(this).val())

    const product = new Product({ id: productId })
    CART_DATA.pos.addProduct(product, quantity)
    CART_DATA.pos.compute()
    localStorage.setItem('CART_DATA', JSON.stringify(CART_DATA))

    let posdetail = CART_DATA.pos.getPOSDetail(productId)
    let quantity_sub_price_unit = posdetail.sub_price_unit * posdetail.quantity
    let quantity_price = posdetail.price_unit * posdetail.quantity
    if (quantity_sub_price_unit) {
      $cartItem.find('.colmoney strong').html(quantity_sub_price_unit.toLocaleString()+'₫')
      $cartItem.find('.colmoney span').html(quantity_price.toLocaleString()+'₫')
    } else {
      $cartItem.find('.colmoney strong').html(quantity_price.toLocaleString()+'₫')
    }

    $('.pos-detail-count').html(CART_DATA.pos.posdetails.length)
    $('.pos-amount-price').html(CART_DATA.pos.amount_price.toLocaleString() + 'đ')
    $('.pos-amount-sub-total').html(CART_DATA.pos.amount_sub_total.toLocaleString() + 'đ')
    $('.pos-amount-total').html(CART_DATA.pos.amount_total.toLocaleString() + 'đ')
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