$(document).ready(function () {
  function reRenderCart(result) {
    $('.cart-sum-item').html(result.order_count)
    $('.cart-amount-price').html(result.order.amount_price.toLocaleString() + 'đ')
    $('.cart-amount-sub-total').html(result.order.amount_sub_total.toLocaleString() + 'đ')
    $('.cart-amount-total').html(result.order.amount_total.toLocaleString() + 'đ')
    $('.cart-amount-discount-total').html(result.order.amount_discount_total.toLocaleString() + 'đ')
  }

  $('.buy').on('click', function (e) {
    const $products = $(this).parents('.product')
    if ($products.length) {
      const $product = $($products[0])
      const productId = $product.data('product-id')
      SERVICES.addToCartRequest({
        data: { product_id: productId },
        success: function (result) {
          reRenderCart(result)
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
        reRenderCart(result)
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
        if (result.orderdetail.sub_price_unit) {
          $cartItem.find('.colmoney strong').html(result.orderdetail.sub_total.toLocaleString()+'₫')
          $cartItem.find('.colmoney span').html(result.orderdetail.amount_price.toLocaleString()+'₫')
          reRenderCart(result)
        } else {
          $cartItem.find('.colmoney strong').html(result.orderdetail.sub_total.toLocaleString()+'₫')
          reRenderCart(result)
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
