var cart = [];

function addToCart(itemId, itemName, itemPrice) {
    // check if item already exists in cart
    for (var i = 0; i < cart.length; i++) {
        if (cart[i].id == itemId) {
            // item already exists, update quantity
            cart[i].quantity += 1;
            updateCart();
            return;
        }
    }

    // item doesn't exist in cart, add it
    cart.push({
        id: itemId,
        name: itemName,
        price: parseFloat(itemPrice).toFixed(2),
        quantity: 1
    });
    

    updateCart();
}

function updateCart() {
    var total = 0;
    var cartHTML = '<ul>';
    for (var i = 0; i < cart.length; i++) {
        total += parseFloat(cart[i].price) * cart[i].quantity;
        cartHTML += '<li>';
        cartHTML += cart[i].name + ' - $' + cart[i].price + ' x ' + cart[i].quantity + '</li>';
    }
    cartHTML += '</ul>';
    cartHTML += '<p>Total: $' + total.toFixed(2) + '</p>';

    document.getElementById("cart").innerHTML = "Cart: " + cart.length + " items" + cartHTML;
}

function sendCartToCheckout() {
    // Convert the cart data to JSON
    var cartData = JSON.stringify(cart);

    // Create a new form element
    var form = document.createElement("form");
    form.setAttribute("method", "POST");
    form.setAttribute("action", "/checkout");

    // Create a hidden input field to hold the cart data
    var cartInput = document.createElement("input");
    cartInput.setAttribute("type", "hidden");
    cartInput.setAttribute("name", "cart");
    cartInput.setAttribute("value", cartData);

    // Add the input field to the form
    form.appendChild(cartInput);

    // Add the form to the document and submit it
    document.body.appendChild(form);
    form.submit();
}
