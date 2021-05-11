const preventInvalidAuthentication = ({ store, redirect }) => {
  if (store.state.auth.loggedIn) {
    return redirect('/')
  }
}

export default preventInvalidAuthentication
