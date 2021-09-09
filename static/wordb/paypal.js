function initPayPalButton() {
  var itemOptions = document.querySelector("#smart-button-container #item-options");
var orderDescription = 'If you like Words2URL, please support us from below.';
if(orderDescription === '') {
orderDescription = 'Item';
}
paypal.Buttons({
style: {
  shape: 'rect',
  color: 'gold',
  layout: 'vertical',
  label: 'paypal',
  
},
createOrder: function(data, actions) {
  var selectedItemDescription = itemOptions.options[itemOptions.selectedIndex].value;
  var selectedItemPrice = parseFloat(itemOptions.options[itemOptions.selectedIndex].getAttribute("price"));
  var priceTotal = selectedItemPrice
  priceTotal = Math.round(priceTotal * 100) / 100;

  return actions.order.create({
    purchase_units: [{
      description: orderDescription,
      amount: {
        currency_code: 'USD',
        value: priceTotal,
      },
    }]
  });
},
onApprove: function(data, actions) {
  return actions.order.capture().then(function(orderData) {
    // Full available details
    console.log('Capture result', orderData, JSON.stringify(orderData, null, 2));
    // Show a success message within this page, e.g.
    const element = document.getElementById('paypal-button-container');
    element.innerHTML = '';
    element.innerHTML = '<h3>Thank you for your support!</h3>';
    // Or go to another URL:  actions.redirect('thank_you.html');
  });
},
onError: function(err) {
  console.log(err);
},
}).render('#paypal-button-container');
}
initPayPalButton();
