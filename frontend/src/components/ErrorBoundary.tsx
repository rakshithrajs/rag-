import { Component, type ErrorInfo, type ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null, errorInfo: null }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ error, errorInfo })
    // eslint-disable-next-line no-console
    console.error('Caught runtime error:', error, errorInfo)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-background p-6 text-foreground">
          <div className="max-w-2xl rounded-lg border border-destructive bg-card p-6 shadow-sm">
            <h1 className="mb-2 text-xl font-semibold text-destructive">
              Something went wrong
            </h1>
            <p className="mb-4 text-sm text-muted-foreground">
              The UI crashed. Details are below to help debug.
            </p>
            <pre className="overflow-auto rounded-md bg-muted p-3 text-xs">
              {this.state.error.toString()}
              {'\n'}
              {this.state.errorInfo?.componentStack}
            </pre>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}
