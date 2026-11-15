import { Link } from 'react-router'

// Shown for any address that is not one of the app's pages
function NotFoundPage() {
  return (
    <section>
      <h1>Page not found</h1>
      <p>
        <Link to="/student">Go to the student page</Link>
      </p>
    </section>
  )
}

export default NotFoundPage
