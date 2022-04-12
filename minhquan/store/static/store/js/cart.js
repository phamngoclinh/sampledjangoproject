function POS ({ total = 0, posdetails = [] }) {
  this.total = parseInt(total)
  this.posdetails = posdetails

  this.compute = function () {
    let total = 0
    this.posdetails.forEach(function (posdetail) { total += posdetail.sub_total })
    this.total = total
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
  this.discount_price = this.product.discount_price
  this.price = this.product.price
  this.sub_total = this.discount_price
                    ? this.discount_price * this.quantity
                    : this.price * this.quantity

  this.setQuantity = function (quantity) {
    this.quantity = parseInt(quantity)
    this.computeSubTotal()
  }

  this.computeSubTotal = function () {
    this.sub_total = this.discount_price
                      ? this.discount_price * this.quantity
                      : this.price * this.quantity
  }
}

function Product ({ id, name, slug, image, price, url = '', discount_price = 0 }) {
  this.id = id
  this.name = name
  this.slug = slug
  this.image = image
  this.price = parseInt(price)
  this.discount_price = parseInt(discount_price)
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
    const posModel = new POS({ total: dataJson.pos.total, posdetails })
    dataModel.pos = posModel
  }

  return dataModel
}()

$(document).ready(function () {
  // Cart top
  $('.pos-detail-count').html(CART_DATA.pos.posdetails.length)
  $('.pos-total').html(CART_DATA.pos.total.toLocaleString() + 'đ')

  // Cart
  $.each(CART_DATA.pos.posdetails, function (index, posdetail) {
    let price = `<strong class="currency">${(posdetail.price * posdetail.quantity).toLocaleString()}đ</strong>`
    if (posdetail.discount_price) {
      price = `
        <strong class="currency">${(posdetail.discount_price * posdetail.quantity).toLocaleString()}đ</strong>
        <span class="price-discount currency">${(posdetail.price * posdetail.quantity).toLocaleString()}₫</span>
      `
    }
    $('.cart-list').prepend(`
      <div
        class="cart-item item"
        data-posdetail-id="${posdetail.id}"
        data-posdetail-quantity="${posdetail.quantity}"
        data-product-id="${posdetail.product.id}"
        data-product-price="${posdetail.product.price}"
        data-product-discount-price="${posdetail.product.discount_price}"
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
        discount_price: $product.data('product-discount-price'),
        url: $product.data('product-url'),
      })
      CART_DATA.pos.addProduct(product)
      CART_DATA.pos.compute()
      localStorage.setItem('CART_DATA', JSON.stringify(CART_DATA))

      $('.pos-total').html(CART_DATA.pos.total.toLocaleString() + 'đ')
      $('.pos-detail-count').html(CART_DATA.pos.posdetails.length)
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
    $('.pos-total').html(CART_DATA.pos.total.toLocaleString() + 'đ')
    $('.pos-detail-count').html(CART_DATA.pos.posdetails.length)
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
    let quantity_discount_price = posdetail.discount_price * posdetail.quantity
    let quantity_price = posdetail.price * posdetail.quantity
    if (quantity_discount_price) {
      $cartItem.find('.colmoney strong').html(quantity_discount_price.toLocaleString()+'₫')
      $cartItem.find('.colmoney span').html(quantity_price.toLocaleString()+'₫')
    } else {
      $cartItem.find('.colmoney strong').html(quantity_price.toLocaleString()+'₫')
    }

    $('.pos-total').html(CART_DATA.pos.total.toLocaleString() + 'đ')
    $('.pos-detail-count').html(CART_DATA.pos.posdetails.length)
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