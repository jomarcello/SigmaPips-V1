"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const dotenv_1 = require("dotenv");
const index_1 = require("./index");
const config_1 = require("./config");
const dataflow_test_1 = require("./dataflow-test");
const script_validators_1 = require("./script-validators");
dotenv_1.default.config();
const app = (0, express_1.default)();
const port = process.env.PORT || 3000;
const validationService = new index_1.ValidationService(process.env.GITHUB_TOKEN);
app.get('/health', (req, res) => {
    res.json({ status: 'healthy' });
});
app.get('/validate-all', async (req, res) => {
    try {
        const results = await Promise.all(config_1.serviceConfigs.map(config => validationService.validateService(config)));
        res.json({ results });
    }
    catch (error) {
        res.status(500).json({ error: 'Validation failed' });
    }
});
app.get('/test-dataflow', async (req, res) => {
    try {
        const result = await (0, dataflow_test_1.testCompleteDataFlow)();
        res.json({ success: result });
    }
    catch (error) {
        res.status(500).json({ error: 'Dataflow test failed' });
    }
});
app.get('/validate-scripts', async (req, res) => {
    try {
        const results = await Promise.all([
            (0, script_validators_1.validateSignalProcessor)(),
            (0, script_validators_1.validateAISignalProcessor)(),
            (0, script_validators_1.validateNewsProcessor)(),
            (0, script_validators_1.validateChartService)(),
            (0, script_validators_1.validateTelegramService)(),
            (0, script_validators_1.validateSubscriberMatcher)()
        ]);
        const allSuccess = results.every(result => result.status === 'success');
        res.json({
            overallStatus: allSuccess ? 'success' : 'failed',
            results
        });
    }
    catch (error) {
        res.status(500).json({
            overallStatus: 'error',
            error: error.message
        });
    }
});
app.listen(port, () => {
    console.log(`Validation service running on port ${port}`);
});
//# sourceMappingURL=server.js.map