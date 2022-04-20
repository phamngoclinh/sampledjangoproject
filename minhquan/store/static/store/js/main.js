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

  // Handle category item click
  $('.cate-list .cate-item').on('click', function () {
    const $groupProduct = $(this).parents('.groupfeature')

    $groupProduct.find('.cate-item').removeClass('active')
    $(this).addClass('active')

    categorySlug = $(this).data('category-slug')
    categoryChildrenSlug = $(this).data('category-chilrens').split(',')

    $groupProduct.find('.product-item').addClass('hidden')

    $productItems = $groupProduct.find('.product-item')
    $productItems.each(function (index, value) {
      const $productItem = $(this)
      productCategorySlug = $productItem.data('product-category')
      if (productCategorySlug === categorySlug || categoryChildrenSlug.includes(productCategorySlug)) {
        $productItem.removeClass('hidden')
      }
    })
  })

  // Handle parent menu in sidebar click
  $('.menu-hover .nav-parent').on('click', function () {
    const $cartItem = $(this).parent('.CateItem')
    $(this).toggleClass('collapse')
    $cartItem.find('.nav-item').toggle()
  })
})