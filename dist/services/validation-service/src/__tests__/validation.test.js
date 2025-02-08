"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const index_1 = require("../index");
const axios_1 = require("axios");
const rest_1 = require("@octokit/rest");
jest.mock('axios');
jest.mock('@octokit/rest');
describe('ValidationService', () => {
    let validationService;
    beforeEach(() => {
        validationService = new index_1.ValidationService('test-token');
    });
    it('should check GitHub repo status', async () => {
        const mockGet = jest.fn().mockResolvedValue({ data: {} });
        rest_1.Octokit.mockImplementation(() => ({
            repos: { get: mockGet }
        }));
        const result = await validationService.validateService({
            name: 'Test Service',
            githubRepo: 'test-repo',
            railwayUrl: 'http://test.url',
            expectedEndpoints: ['/test']
        });
        expect(result.githubStatus).toBe(true);
        expect(mockGet).toHaveBeenCalledWith({
            owner: 'your-org',
            repo: 'test-repo'
        });
    });
    it('should check Railway deployment status', async () => {
        axios_1.default.get.mockResolvedValueOnce({ status: 200 });
        const result = await validationService.validateService({
            name: 'Test Service',
            githubRepo: 'test-repo',
            railwayUrl: 'http://test.url',
            expectedEndpoints: ['/test']
        });
        expect(result.railwayStatus).toBe(true);
        expect(axios_1.default.get).toHaveBeenCalledWith('http://test.url/health');
    });
});
//# sourceMappingURL=validation.test.js.map