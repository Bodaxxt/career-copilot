interface CareerCardProps {
  title: string;
  description: string;
  icon: string;
}

export function CareerCard({ title, description, icon }: CareerCardProps) {
  return (
    <div className="p-6 rounded-2xl border border-white/10 bg-slate-900/60 backdrop-blur-xl hover:border-indigo-500/40 transition-all text-right shadow-lg">
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
      <p className="text-slate-400 text-sm leading-relaxed">{description}</p>
    </div>
  );
}
