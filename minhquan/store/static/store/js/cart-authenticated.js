$(document).ready(function () {
  $('.buy').on('click', function (e) {
    const $products = $(this).parents('.product')
    if ($products.length) {
      const $product = $($products[0])
      const productId = $product.data('product-id')
      SERVICES.addToCartRequest({
        data: { product_id: productId },
        success: function (result) {
          $('.pos-total').html(result.pos.total.toLocaleString() + 'đ')
          $('.pos-detail-count').html(result.pos_count)
        }
      })
    }
  })

  $('.cart-item .delete').on('click', function () {
    const $cartItem = $(this).parents('.cart-item')
    const productId = $cartItem.data('product-id')
    SERVICES.addToCartRequest({
      data: { product_id: productId, quantity: 0 },
      success: function (result) {
        $cartItem.remove()
        $('.pos-total').html(result.pos.total.toLocaleString() + 'đ')
        $('.pos-detail-count').html(result.pos_count)
      }
    })
  })

  $('.cart-item .quantity .qty').on('change', function () {
    const $cartItem = $(this).parents('.cart-item')
    const productId = $cartItem.data('product-id')
    const quantity = parseInt($(this).val())
    SERVICES.addToCartRequest({
      data: { product_id: productId, quantity: quantity > 0 ? quantity : 0 },
      success: function (result) {
        let quantity_discount_price = result.product.discount_price * result.posdetail.quantity
        let quantity_price = result.product.price * result.posdetail.quantity
        if (quantity_discount_price) {
          $cartItem.find('.colmoney strong').html(quantity_discount_price.toLocaleString()+'₫')
          $cartItem.find('.colmoney span').html(quantity_price.toLocaleString()+'₫')
          $('.pos-total').html(result.pos.total.toLocaleString() + 'đ')
          $('.pos-detail-count').html(result.pos_count)
        } else {
          $cartItem.find('.colmoney strong').html(quantity_price.toLocaleString()+'₫')
          $('.pos-total').html(result.pos.total.toLocaleString() + 'đ')
          $('.pos-detail-count').html(result.pos_count)
        }
      }
    })
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
