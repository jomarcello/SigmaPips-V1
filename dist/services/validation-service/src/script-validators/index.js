"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateSignalProcessor = validateSignalProcessor;
exports.validateAISignalProcessor = validateAISignalProcessor;
exports.validateNewsProcessor = validateNewsProcessor;
exports.validateChartService = validateChartService;
exports.validateTelegramService = validateTelegramService;
exports.validateSubscriberMatcher = validateSubscriberMatcher;
const axios_1 = require("axios");
async function validateSignalProcessor() {
    try {
        const webhookResponse = await axios_1.default.post('https://tradingview-signal-processor-production.up.railway.app/webhook', {
            symbol: 'BTCUSDT',
            interval: '1h',
            strategy: 'TEST_VALIDATION'
        });
        const signalId = webhookResponse.data.signalId;
        const newsResponse = await axios_1.default.get(`https://tradingview-signal-processor-production.up.railway.app/news/${signalId}`);
        return {
            scriptName: 'Signal Entry + News Scraper',
            status: 'success',
            details: {
                functionalityWorking: true,
                lastRunTime: new Date(),
            }
        };
    }
    catch (error) {
        return {
            scriptName: 'Signal Entry + News Scraper',
            status: 'failed',
            details: {
                functionalityWorking: false,
                errors: [error.message]
            }
        };
    }
}
async function validateAISignalProcessor() {
    try {
        const testSignal = {
            symbol: 'BTCUSDT',
            interval: '1h',
            strategy: 'TEST_VALIDATION'
        };
        const response = await axios_1.default.post('https://tradingview-signal-ai-service-production.up.railway.app/process-signal', testSignal);
        const aiOutput = response.data;
        const isValidOutput = aiOutput.analysis && aiOutput.recommendation;
        return {
            scriptName: 'AI Signal Processor',
            status: isValidOutput ? 'success' : 'failed',
            details: {
                functionalityWorking: isValidOutput,
                lastRunTime: new Date()
            }
        };
    }
    catch (error) {
        return {
            scriptName: 'AI Signal Processor',
            status: 'failed',
            details: {
                functionalityWorking: false,
                errors: [error.message]
            }
        };
    }
}
async function validateNewsProcessor() {
    try {
        const testNews = {
            articles: [
                {
                    title: "Test Article",
                    content: "This is a test article for validation purposes."
                }
            ]
        };
        const response = await axios_1.default.post('https://tradingview-news-ai-service-production.up.railway.app/process-news', testNews);
        const isValidSummary = response.data.summary && response.data.sentiment;
        return {
            scriptName: 'AI News Processor',
            status: isValidSummary ? 'success' : 'failed',
            details: {
                functionalityWorking: isValidSummary,
                lastRunTime: new Date()
            }
        };
    }
    catch (error) {
        return {
            scriptName: 'AI News Processor',
            status: 'failed',
            details: {
                functionalityWorking: false,
                errors: [error.message]
            }
        };
    }
}
async function validateChartService() {
    try {
        const testRequest = {
            symbol: 'BTCUSDT',
            interval: '1h'
        };
        const response = await axios_1.default.post('https://tradingview-chart-service-production.up.railway.app/generate-chart', testRequest);
        const hasImage = response.data.imageUrl || response.data.image;
        return {
            scriptName: 'TradingView Chart Service',
            status: hasImage ? 'success' : 'failed',
            details: {
                functionalityWorking: hasImage,
                lastRunTime: new Date()
            }
        };
    }
    catch (error) {
        return {
            scriptName: 'TradingView Chart Service',
            status: 'failed',
            details: {
                functionalityWorking: false,
                errors: [error.message]
            }
        };
    }
}
async function validateTelegramService() {
    try {
        const testMessage = {
            chatId: 'TEST_CHAT_ID',
            message: 'Test validation message',
            type: 'validation'
        };
        const response = await axios_1.default.post('https://tradingview-telegram-service-production.up.railway.app/send', testMessage);
        return {
            scriptName: 'Telegram Send Service',
            status: 'success',
            details: {
                functionalityWorking: true,
                lastRunTime: new Date()
            }
        };
    }
    catch (error) {
        return {
            scriptName: 'Telegram Send Service',
            status: 'failed',
            details: {
                functionalityWorking: false,
                errors: [error.message]
            }
        };
    }
}
async function validateSubscriberMatcher() {
    try {
        const testSignal = {
            symbol: 'BTCUSDT',
            strategy: 'TEST_STRATEGY'
        };
        const response = await axios_1.default.post('https://sup-abase-subscriber-matcher-production.up.railway.app/match', testSignal);
        const hasSubscribers = Array.isArray(response.data.subscribers);
        return {
            scriptName: 'Subscriber Matcher',
            status: hasSubscribers ? 'success' : 'failed',
            details: {
                functionalityWorking: hasSubscribers,
                lastRunTime: new Date()
            }
        };
    }
    catch (error) {
        return {
            scriptName: 'Subscriber Matcher',
            status: 'failed',
            details: {
                functionalityWorking: false,
                errors: [error.message]
            }
        };
    }
}
//# sourceMappingURL=index.js.map