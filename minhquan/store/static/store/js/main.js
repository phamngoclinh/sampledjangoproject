$(document).ready(function () {
  // Synchrozire local shopping_cart with database
  const $shoppingCartData = $('.shopping-cart-data')
  if ($shoppingCartData.length) {
    $shoppingCartData.val(JSON.stringify(CART_DATA))
  }

  // Handle before logout
  $('.logout-action').on('click', function () {
    localStorage.removeItem('CART_DATA')
    window.location.href = $(this).data('url')
  })
})