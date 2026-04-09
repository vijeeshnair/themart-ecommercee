function updateCartCount() {
    const cartCount = document.querySelector('.cart-count');
    if (cartCount) {
        fetch('/api/cart/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            cartCount.textContent = data.count || '0';
        })
        .catch(() => {
            cartCount.textContent = '0';
        });
    }
}

function addToCart(productId) {
    const quantity = document.getElementById('quantity') ? parseInt(document.getElementById('quantity').value) : 1;
    
    fetch('/api/cart/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({product_id: productId, quantity: quantity})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Product added to cart!', 'success');
            updateCartCount();
            setTimeout(() => location.reload(), 1000);
        }
    })
    .catch(error => {
        showNotification('Error adding to cart', 'error');
    });
}

function updateCartQuantity(productId, quantity) {
    fetch('/api/cart/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({product_id: productId, quantity: quantity})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

function removeFromCart(productId) {
    if (confirm('Are you sure you want to remove this item?')) {
        fetch('/api/cart/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({product_id: productId})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    }
}

function viewProduct(productId) {
    window.location.href = `/product/${productId}`;
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#46C389' : '#FF8F9C'};
        color: white;
        border-radius: 5px;
        z-index: 9999;
    `;
    
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();
    
    document.querySelectorAll('.minus').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            const input = document.querySelector(`.qty-input[data-id="${id}"]`);
            if (input && parseInt(input.value) > 1) {
                input.value = parseInt(input.value) - 1;
                updateCartQuantity(id, input.value);
            }
        });
    });
    
    document.querySelectorAll('.plus').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            const input = document.querySelector(`.qty-input[data-id="${id}"]`);
            if (input) {
                input.value = parseInt(input.value) + 1;
                updateCartQuantity(id, input.value);
            }
        });
    });
    
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            removeFromCart(id);
        });
    });
});
