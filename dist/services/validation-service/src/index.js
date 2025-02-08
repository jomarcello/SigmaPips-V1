"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ValidationService = void 0;
const axios_1 = require("axios");
const rest_1 = require("@octokit/rest");
class ValidationService {
    constructor(githubToken) {
        this.githubToken = githubToken;
        this.octokit = new rest_1.Octokit({ auth: githubToken });
    }
    async validateService(config) {
        const results = {
            name: config.name,
            githubStatus: await this.checkGithubRepo(config.githubRepo),
            railwayStatus: await this.checkRailwayDeployment(config.railwayUrl),
            endpointsStatus: await this.checkEndpoints(config.railwayUrl, config.expectedEndpoints)
        };
        return results;
    }
    async checkGithubRepo(repo) {
        try {
            await this.octokit.repos.get({
                owner: 'your-org',
                repo: repo
            });
            return true;
        }
        catch (_a) {
            return false;
        }
    }
    async checkRailwayDeployment(url) {
        try {
            const response = await axios_1.default.get(`${url}/health`);
            return response.status === 200;
        }
        catch (_a) {
            return false;
        }
    }
    async checkEndpoints(baseUrl, endpoints) {
        const results = {};
        for (const endpoint of endpoints) {
            try {
                const response = await axios_1.default.get(`${baseUrl}${endpoint}`);
                results[endpoint] = response.status === 200;
            }
            catch (_a) {
                results[endpoint] = false;
            }
        }
        return results;
    }
}
exports.ValidationService = ValidationService;
//# sourceMappingURL=index.js.map