'use client';
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = Sidebar;
const lucide_react_1 = require("lucide-react");
const link_1 = require("next/link");
const navigation_1 = require("next/navigation");
const utils_1 = require("@/lib/utils");
const navItems = [
    { icon: lucide_react_1.Home, label: 'Home', href: '/home' },
    { icon: lucide_react_1.ShoppingBag, label: 'Orders', href: '/orders' },
    { icon: lucide_react_1.Calendar, label: 'Kalender', href: '/calendar' },
    { icon: lucide_react_1.FileText, label: 'Documenten', href: '/documents' },
    { icon: lucide_react_1.PieChart, label: 'Rapporten', href: '/reports' },
    { icon: lucide_react_1.Users, label: 'Gebruikers', href: '/users' },
];
function Sidebar() {
    const pathname = (0, navigation_1.usePathname)();
    return (<aside className="w-20 bg-white border-r border-gray-200 flex flex-col items-center py-4">
      {navItems.map((item) => (<link_1.default key={item.href} href={item.href} className={(0, utils_1.cn)("p-3 rounded-lg mb-2 hover:bg-gray-100", pathname === item.href ? "bg-gray-100" : "")}>
          <item.icon className="w-6 h-6 text-gray-600"/>
        </link_1.default>))}
    </aside>);
}
//# sourceMappingURL=Sidebar.js.map