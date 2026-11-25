import type { ReactNode } from 'react'
import { BusIcon } from './icons'
import RouteArt from './RouteArt'

type Props = {
  children: ReactNode
}

// The frame shared by Sign in and Sign up (#68): the route picture, the SmartBus logo and the
// one-line promise, then the page's own form
function AuthLayout({ children }: Props) {
  return (
    <section className="auth">
      <div className="auth-art">
        <RouteArt />
      </div>
      <div className="auth-body">
        <div className="brand">
          <span className="brand-mark">
            <BusIcon size={30} />
          </span>
          <span className="brand-name">
            <strong>SmartBus</strong>
            <span>African Leadership University</span>
          </span>
        </div>
        <p className="tagline">
          See your bus live, know when it reaches your stop, and board with one scan.
        </p>
        {children}
      </div>
    </section>
  )
}

export default AuthLayout
