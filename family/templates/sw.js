// sw.js (Template)

self.addEventListener('install', function (event) {
    self.skipWaiting();
});

self.addEventListener('activate', function (event) {
    event.waitUntil(clients.claim());
});

self.addEventListener('fetch', function (event) {
    // Basic fetch listener required for PWA installability
    event.respondWith(fetch(event.request));
});

self.addEventListener('push', function (event) {
    const eventData = event.data ? event.data.json() : {};
    const title = eventData.head || 'New Notification';
    const options = {
        body: eventData.body || 'You have a new update.',
        icon: eventData.icon || '/static/images/favicon.png',
        badge: '/static/images/favicon.png',
        data: {
            url: eventData.url || '/'
        }
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow(event.notification.data.url)
    );
});
