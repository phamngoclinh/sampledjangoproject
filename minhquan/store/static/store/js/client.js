function sendRequest({ data, ...others }) {

  $.ajax({
    method: 'GET',
    url: '/',
    data: JSON.stringify({
      ...data,
      ...post_data
    }),
    fail: function (e) {
      alert('failed')
    },
    success: function (result) {
      console.log('result', result)
    },
    ...others,
  })
}

function addToCartRequest({ data, ...others }) {
  sendRequest({ method: 'POST', url: '/add-to-cart/', data, ...others })
}