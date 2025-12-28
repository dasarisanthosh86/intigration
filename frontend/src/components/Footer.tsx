const Footer = () => {
  return (
    <footer className="bg-black border-t border-zinc-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-1.5 rounded-lg bg-accent/20 text-accent">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span className="text-xl font-bold text-white">Antigravity</span>
            </div>
            <p className="text-zinc-500 max-w-sm text-sm leading-relaxed">
              Professional software development lifecycle management.
              Built for speed, security, and developer happiness.
            </p>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Platform</h4>
            <ul className="space-y-3 text-sm text-zinc-500">
              <li className="hover:text-accent transition-colors cursor-pointer">Project Management</li>
              <li className="hover:text-accent transition-colors cursor-pointer">Code Review</li>
              <li className="hover:text-accent transition-colors cursor-pointer">Deployments</li>
              <li className="hover:text-accent transition-colors cursor-pointer">Analytics</li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">Company</h4>
            <ul className="space-y-3 text-sm text-zinc-500">
              <li className="hover:text-accent transition-colors cursor-pointer">About Us</li>
              <li className="hover:text-accent transition-colors cursor-pointer">Careers</li>
              <li className="hover:text-accent transition-colors cursor-pointer">Blog</li>
              <li className="hover:text-accent transition-colors cursor-pointer">Contact</li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-zinc-900 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-zinc-600">
            © 2025 Antigravity Enterprise SDLC Platform. All rights reserved.
          </p>
          <div className="flex gap-6">
            <a href="#" className="text-zinc-600 hover:text-white transition-colors">Privacy</a>
            <a href="#" className="text-zinc-600 hover:text-white transition-colors">Terms</a>
            <a href="#" className="text-zinc-600 hover:text-white transition-colors">Security</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;