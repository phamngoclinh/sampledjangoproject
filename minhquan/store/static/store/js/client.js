const HTTP_CLIENT = {
  sendRequest: function ({ data, ...others }) {
    $.ajax({
      method: 'GET',
      url: '/',
      data: JSON.stringify({
        ...data,
        'csrfmiddlewaretoken': CSRF_TOKEN
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
}

const SERVICES = {
  addToCartRequest: function ({ data, ...others }) {
    HTTP_CLIENT.sendRequest({ method: 'POST', url: '/add-to-cart/', data, ...others })
  }
}