import { useMemo } from 'react';

const STATE_LABELS = {
  idle: '',
  explode: '💥 炸开',
  textClaude: '✨ claude code',
  holdClaude: '✨ claude code',
  textLove: '💖 love life',
  holdLove: '💖 love life'
};

export default function StatusDisplay({ fingerCount, animState }) {
  const label = useMemo(() => STATE_LABELS[animState] || '', [animState]);

  return (
    <div className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5
                    text-white/60 text-xs font-mono tracking-wider
                    pointer-events-none select-none">
      <span className={`w-2 h-2 rounded-full transition-all duration-300
        ${fingerCount > 0 ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]' : 'bg-white/20'}`} />
      <span>{fingerCount > 0 ? `${fingerCount} 指` : '待机'}</span>
      {label && <span className="text-white/80">{label}</span>}
    </div>
  );
}
