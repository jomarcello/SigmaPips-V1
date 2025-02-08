import { SignalService } from '../services/signal.service';
export declare class SignalController {
    private readonly signalService;
    constructor(signalService: SignalService);
    handleSignal(data: any): Promise<any>;
}
