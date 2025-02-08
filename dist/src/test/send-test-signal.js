"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const amqplib_1 = require("amqplib");
async function sendTestSignal() {
    try {
        const connection = await amqplib_1.default.connect('amqp://localhost:5672');
        const channel = await connection.createChannel();
        const testSignal = {
            symbol: 'BTCUSDT',
            type: 'LONG',
            price: 50000,
            timestamp: new Date().toISOString()
        };
        await channel.assertQueue('signal_processing_queue');
        channel.sendToQueue('signal_processing_queue', Buffer.from(JSON.stringify(testSignal)));
        console.log('Test signal sent:', testSignal);
        setTimeout(() => {
            connection.close();
            process.exit(0);
        }, 500);
    }
    catch (error) {
        console.error('Error:', error);
        process.exit(1);
    }
}
sendTestSignal();
//# sourceMappingURL=send-test-signal.js.map