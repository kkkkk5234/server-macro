// Khởi tạo Telegram WebApp
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

// Biến toàn cục
let currentUser = null;
let currentMenu = 'main';

// Lấy thông tin user từ Telegram
const userData = tg.initDataUnsafe.user || {};
const initData = tg.initData;

// Khởi tạo
document.addEventListener('DOMContentLoaded', async () => {
    await loadUserInfo();
    await loadMainMenu();
});

// Gọi API
async function apiRequest(endpoint, method = 'GET', data = null) {
    const headers = {
        'Content-Type': 'application/json',
        'X-Telegram-Init-Data': initData
    };
    
    const options = {
        method,
        headers,
        body: data ? JSON.stringify(data) : null
    };
    
    const response = await fetch(`/api${endpoint}`, options);
    const result = await response.json();
    
    if (!response.ok) {
        throw new Error(result.detail || 'Có lỗi xảy ra');
    }
    
    return result;
}

// Lấy thông tin user
async function loadUserInfo() {
    try {
        const user = await apiRequest('/auth/me');
        currentUser = user;
        
        const userInfo = document.getElementById('user-info');
        userInfo.innerHTML = `
            <div class="user-card">
                <span>👤 ${user.first_name || 'User'}</span>
                <span>💰 ${formatNumber(user.balance.balance)}đ</span>
                ${user.is_admin ? '<span class="badge-admin">👑 Admin</span>' : ''}
                ${user.is_customer ? '<span class="badge-pro">⭐ Pro</span>' : ''}
            </div>
        `;
    } catch (error) {
        console.error('Error loading user:', error);
    }
}

// Tải menu chính
async function loadMainMenu() {
    const menuContainer = document.getElementById('main-menu');
    
    try {
        // Kiểm tra admin
        if (currentUser && currentUser.is_admin) {
            const adminMenu = await apiRequest('/admin/menu');
            menuContainer.innerHTML = renderMenu(adminMenu.menu, 'admin');
        } else {
            const userMenu = await apiRequest('/user/menu');
            menuContainer.innerHTML = renderMenu(userMenu.menu, 'user');
        }
    } catch (error) {
        console.error('Error loading menu:', error);
    }
}

// Render menu
function renderMenu(menu, type) {
    return menu.map(item => `
        <button class="menu-item" onclick="handleAction('${item.action}')">
            <span class="menu-icon">${item.icon}</span>
            <span class="menu-name">${item.name}</span>
        </button>
    `).join('');
}

// Xử lý action
async function handleAction(action) {
    const content = document.getElementById('content');
    
    switch(action) {
        case 'deposit':
            await showDepositForm();
            break;
        case 'rent_pro':
            await showRentProMenu();
            break;
        case 'games':
            await showGamesMenu();
            break;
        case 'mmo':
            await showProducts();
            break;
        case 'rai_link':
            await showRaiLinkMenu();
            break;
        case 'tracking_fb':
            await showTrackingFBMenu();
            break;
        case 'tracking_tiktok':
            await showTrackingTikTokMenu();
            break;
        case 'list_customers':
            await showCustomersList();
            break;
        case 'maintenance':
            await showMaintenanceMenu();
            break;
        case 'add_product':
            await showAddProductForm();
            break;
        case 'delivery_manage':
            await showDeliveryManage();
            break;
        case 'approve_deposit':
            await showPendingDeposits();
            break;
        case 'announce':
            await showAnnounceForm();
            break;
        default:
            content.innerHTML = '<p>Chức năng chưa phát triển!</p>';
    }
}

// Helper: format số
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Hiển thị form nạp tiền
async function showDepositForm() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>💰 Nạp Tiền</h2>
        <div class="balance-info">
            <p>Số dư hiện tại: <strong>${formatNumber(currentUser.balance.balance)}đ</strong></p>
            <p>Đã nạp: ${formatNumber(currentUser.balance.total_deposited)}đ</p>
            <p>Đã dùng: ${formatNumber(currentUser.balance.total_used)}đ</p>
        </div>
        <input type="number" id="deposit-amount" placeholder="Số tiền nạp (tối thiểu 10.000đ)" min="10000">
        <button class="btn-primary" onclick="submitDeposit()">Nạp tiền</button>
    `;
}

// Submit nạp tiền
async function submitDeposit() {
    const amount = parseInt(document.getElementById('deposit-amount').value);
    
    if (!amount || amount < 10000) {
        tg.showAlert('Số tiền nạp tối thiểu là 10.000đ!');
        return;
    }
    
    try {
        const result = await apiRequest('/deposit', 'POST', { amount });
        
        tg.showAlert(`
            💳 THÔNG TIN NẠP TIỀN
            
            Số tiền: ${formatNumber(result.amount)}đ
            Nội dung chuyển khoản: ${result.content}
            
            Chủ tài khoản: ${result.bank_info.account_name}
            Số tài khoản: ${result.bank_info.account_number}
            Ngân hàng: ${result.bank_info.bank_name}
            
            ${result.note}
        `);
        
        await loadUserInfo();
    } catch (error) {
        tg.showAlert(error.message);
    }
}

// Hiển thị menu thuê gói Pro
async function showRentProMenu() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <h2>🔑 Thuê Gói Pro</h2>
        <div class="pro-packages">
            <div class="package-card">
                <h3>15 ngày</h3>
                <p class="price">${formatNumber(19000)}đ</p>
                <button onclick="rentPro(15)">Thuê</button>
            </div>
            <div class="package-card">
                <h3>30 ngày</h3>
                <p class="price">${formatNumber(39000)}đ</p>
                <button onclick="rentPro(30)">Thuê</button>
            </div>
            <div class="package-card">
                <h3>60 ngày</h3>
                <p class="price">${formatNumber(69000)}đ</p>
                <button onclick="rentPro(60)">Thuê</button>
            </div>
        </div>
    `;
}

// Thuê gói Pro
async function rentPro(days) {
    try {
        const result = await apiRequest('/rent_pro', 'POST', { days });
        tg.showAlert(`✅ ${result.message}`);
        await loadUserInfo();
    } catch (error) {
        tg.showAlert(error.message);
    }
}

// ... (tiếp tục các function khác)