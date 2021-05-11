const preventInvalidAccessToAuthenticatedPages = ({ store, redirect }) => {
  if (!store.state.auth.loggedIn) {
    return redirect('/')
  }
}

export default preventInvalidAccessToAuthenticatedPages
