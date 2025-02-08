interface ValidationResponse {
    scriptName: string;
    status: 'success' | 'failed';
    details: {
        functionalityWorking: boolean;
        lastRunTime?: Date;
        errors?: string[];
    };
}
export declare function validateSignalProcessor(): Promise<ValidationResponse>;
export declare function validateAISignalProcessor(): Promise<ValidationResponse>;
export declare function validateNewsProcessor(): Promise<ValidationResponse>;
export declare function validateChartService(): Promise<ValidationResponse>;
export declare function validateTelegramService(): Promise<ValidationResponse>;
export declare function validateSubscriberMatcher(): Promise<ValidationResponse>;
export {};
