import { Link, useLocation } from 'react-router-dom';
import { ROUTES } from '../constants/routes';

const Sidebar = () => {
    const location = useLocation();

    const menuItems = [
        { name: 'SDLC Pipeline', icon: '⚡', path: ROUTES.DASHBOARD },
        { name: 'Repositories', icon: '📁', path: `${ROUTES.DASHBOARD}/repos` },
        { name: 'Documentation', icon: '📄', path: `${ROUTES.DASHBOARD}/docs` },
        { name: 'Analytics', icon: '📊', path: `${ROUTES.DASHBOARD}/analytics` },
        { name: 'Settings', icon: '⚙️', path: `${ROUTES.DASHBOARD}/settings` },
    ];

    return (
        <aside className="w-64 bg-zinc-950/50 backdrop-blur-xl border-r border-white/5 flex flex-col h-[calc(100vh-100px)] fixed left-0 top-24 z-20 m-4 rounded-[2rem]">
            <div className="p-6 border-b border-white/5">
                <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-accent rounded-full animate-pulse" />
                    <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Navigation</span>
                </div>
            </div>

            <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                {menuItems.map((item) => (
                    <Link
                        key={item.path}
                        to={item.path}
                        className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${location.pathname === item.path
                            ? 'bg-accent/10 text-accent'
                            : 'text-zinc-500 hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <span className="text-lg">{item.icon}</span>
                        {item.name}
                    </Link>
                ))}
            </nav>

            <div className="p-4 border-t border-white/5">
                <div className="bg-gradient-to-br from-zinc-900 to-black p-4 rounded-2xl border border-white/5">
                    <p className="text-[10px] font-bold text-accent uppercase tracking-widest mb-2">Cloud Usage</p>
                    <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <div className="w-2/3 h-full bg-accent"></div>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
