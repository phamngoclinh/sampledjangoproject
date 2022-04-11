$(document).ready(function () {
  $('.buy').on('click', function (e) {
    const $products = $(this).parents('.product')
    if ($products.length) {
      const $product = $($products[0])
      const productId = $product.data('product-id')
      addToCartRequest({
        data: { product_id: productId },
        success: function (result) {
          $('#pos_total').html(result.pos.total.toLocaleString() + 'đ')
          $('#pos_detail_count').html(result.pos_count)
        }
      })
    }
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