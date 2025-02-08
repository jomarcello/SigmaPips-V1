"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.testCompleteDataFlow = testCompleteDataFlow;
const axios_1 = require("axios");
async function testCompleteDataFlow() {
    try {
        const signalResponse = await axios_1.default.post('signal-entry-url/webhook', {
            symbol: 'BTCUSDT',
            interval: '1h',
            strategy: 'TEST'
        });
        const signalId = signalResponse.data.signalId;
        await Promise.all([
            checkAIProcessing(signalId),
            checkNewsProcessing(signalId),
            checkTelegramDelivery(signalId)
        ]);
        return true;
    }
    catch (error) {
        console.error('Dataflow test failed:', error);
        return false;
    }
}
async function checkAIProcessing(signalId) {
    try {
        const response = await axios_1.default.get(`${process.env.AI_SERVICE_URL}/status/${signalId}`);
        return response.data.status === 'completed';
    }
    catch (_a) {
        return false;
    }
}
async function checkNewsProcessing(signalId) {
    try {
        const response = await axios_1.default.get(`${process.env.NEWS_SERVICE_URL}/status/${signalId}`);
        return response.data.status === 'completed';
    }
    catch (_a) {
        return false;
    }
}
async function checkTelegramDelivery(signalId) {
    try {
        const response = await axios_1.default.get(`${process.env.TELEGRAM_SERVICE_URL}/delivery/${signalId}`);
        return response.data.delivered === true;
    }
    catch (_a) {
        return false;
    }
}
//# sourceMappingURL=dataflow-test.js.map