'use client';
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = Header;
const lucide_react_1 = require("lucide-react");
const link_1 = require("next/link");
const metrics = [
    { label: 'Omzet deze maand', href: '/revenue-this-month' },
    { label: 'Orders in 2023', href: '/orders-in-2023' },
    { label: 'Refunds in Sep 2023', href: '/refunds-in-sep-2023' },
    { label: 'YoY Groei 2023', href: '/yoy-growth-rate-in-2023' },
    { label: 'Totale Omzet', href: '/total-revenue' },
];
function Header() {
    return (<header className="bg-white border-b border-gray-200 py-4 px-6">
      <div className="flex items-center justify-between">
        <nav className="flex space-x-4">
          {metrics.map((item) => (<link_1.default key={item.href} href={item.href} className="text-sm text-gray-600 hover:text-gray-900">
              {item.label}
            </link_1.default>))}
        </nav>
        
        <div className="relative">
          <lucide_react_1.Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5"/>
          <input type="search" placeholder="Zoeken..." className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"/>
        </div>
      </div>
    </header>);
}
//# sourceMappingURL=Header.js.map