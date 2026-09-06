import { useEffect, useRef } from 'react'

type Props = { className?: string }

export default function KineticGrid({ className = '' }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const context = canvas.getContext('2d')
    if (!context) return
    let frame = 0
    let mouse = { x: -1000, y: -1000 }
    let target = { x: -1000, y: -1000 }

    const resize = () => {
      const ratio = Math.min(window.devicePixelRatio || 1, 2)
      canvas.width = window.innerWidth * ratio
      canvas.height = window.innerHeight * ratio
      canvas.style.width = `${window.innerWidth}px`
      canvas.style.height = `${window.innerHeight}px`
      context.setTransform(ratio, 0, 0, ratio, 0, 0)
    }
    const move = (event: MouseEvent) => { target = { x: event.clientX, y: event.clientY } }
    const draw = () => {
      mouse.x += (target.x - mouse.x) * 0.08
      mouse.y += (target.y - mouse.y) * 0.08
      const width = window.innerWidth
      const height = window.innerHeight
      context.clearRect(0, 0, width, height)
      for (let x = 28; x < width; x += 55) for (let y = 28; y < height; y += 55) {
        const distance = Math.hypot(x - mouse.x, y - mouse.y)
        const active = Math.max(0, 1 - distance / 240)
        const shift = active * 14
        const pointX = x + (x - mouse.x) / (distance || 1) * shift
        const pointY = y + (y - mouse.y) / (distance || 1) * shift
        context.fillStyle = `rgba(20, 63, 69, ${0.08 + active * 0.2})`
        context.beginPath(); context.arc(pointX, pointY, 1 + active * 1.6, 0, Math.PI * 2); context.fill()
        if (x < width - 55) { context.strokeStyle = `rgba(20, 63, 69, ${0.045 + active * 0.12})`; context.beginPath(); context.moveTo(pointX, pointY); context.lineTo(x + 55, y); context.stroke() }
        if (y < height - 55) { context.beginPath(); context.moveTo(pointX, pointY); context.lineTo(x, y + 55); context.stroke() }
      }
      frame = requestAnimationFrame(draw)
    }
    resize(); window.addEventListener('resize', resize); window.addEventListener('mousemove', move); frame = requestAnimationFrame(draw)
    return () => { cancelAnimationFrame(frame); window.removeEventListener('resize', resize); window.removeEventListener('mousemove', move) }
  }, [])

  return <canvas ref={canvasRef} className={`kinetic-grid ${className}`} aria-hidden="true" />
}