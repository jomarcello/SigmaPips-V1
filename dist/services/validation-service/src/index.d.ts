interface ServiceConfig {
    name: string;
    githubRepo: string;
    railwayUrl: string;
    expectedEndpoints: string[];
}
interface ValidationResult {
    name: string;
    githubStatus: boolean;
    railwayStatus: boolean;
    endpointsStatus: Record<string, boolean>;
}
export declare class ValidationService {
    private githubToken;
    private octokit;
    constructor(githubToken: string);
    validateService(config: ServiceConfig): Promise<ValidationResult>;
    private checkGithubRepo;
    private checkRailwayDeployment;
    private checkEndpoints;
}
export {};
